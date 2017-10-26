import asyncio
import os

import re

# from orator import DatabaseManager

from aioweb import ConfigReader
from aioweb.conf import settings

# from orator import Model as OratorModel

from aioweb.core.model import Model

def get_dbconfig():
    environment = os.getenv("AIOWEB_ENV", 'development')

    conf = ConfigReader(f'config/database/{environment}.yml')
    dbconfig = conf.get('databases')

    for env in dbconfig:
        if type(dbconfig[env]) == dict:
            if dbconfig[env]["driver"] == "sqlite":
                dbconfig[env]["database"] = os.path.join(settings.BASE_DIR, f'db/{dbconfig[env]["database"]}')

    if not 'default' in dbconfig:
        dbconfig['default'] = dbconfig[environment]
    return dbconfig


def init_db_engine():
    dbconfig = get_dbconfig()


class DBFactory(object):
    def __init__(self, config):
        self.config = config
        self.pools = {}

    def connection(self, connection=None):
        if connection is None:
            connection = self.config.get('default', 'development')

        if connection in self.pools:
            return self.pools[connection]

        db_config = self.config[connection]
        dbwrapper = None

        if db_config.get('driver') == 'pgsql':
            import aiopg
            from . import pg_extras
            # dbname=aiopg user=aiopg password=passwd host=127.0.0.1
            host_info = []
            if db_config.get('host'):
                host_info.append('host = {}'.format(db_config.get('host')))
            if db_config.get('port'):
                host_info.append('port = {}'.format(db_config.get('port')))
            pool = aiopg.create_pool("dbname={} {} user={} password={}".format(
                db_config.get('database'),
                ' '.join(host_info),
                db_config.get('user'),
                db_config.get('password'),
            ))
            dbwrapper = DBPGWrapper(pool, cursor=pg_extras.PGDictNamedtupleCursor)
        elif db_config.get('driver') == 'sqlite':
            import aioodbc
            pool = aioodbc.create_pool(dsn="Driver=SQLite3;Database={}".format(
                os.path.join(settings.BASE_DIR, 'db', db_config.get('database', 'db.sqlite3'))))
            dbwrapper = DBWrapper(pool)
        self.pools[connection] = dbwrapper
        return dbwrapper

    async def close(self):
        for pool in self.pools:
            self.pools[pool].close()
        for pool in self.pools:
            await self.pools[pool].wait_closed()


class DBConnection(object):
    def __init__(self, factory, default='default'):
        self.factory = factory
        self.default_connection = default
        self.wrappers = {}

    def get_wrapper(self, connection):
        if connection in self.wrappers:
            return self.wrappers[connection]
        return self.factory.connection(connection)

    def __getattr__(self, item):
        return getattr(self.get_wrapper(self.default_connection), item)

    def __call__(self, connection, *args, **kwargs):
        return self.get_wrapper(connection)





async def init_db(app):
    db_conf = get_dbconfig()

    if not db_conf:
        raise ReferenceError('Database configuration does not contain databases domain')

    if not hasattr(app, 'db'):
        setattr(app, 'db', DBConnection(DBFactory(db_conf)))
        setattr(Model, 'db', app.db)
        # setattr(app, 'db', db)


async def close_db(app):
    if hasattr(app, 'db'):
        try:
            app.db.close()
            await app.db.wait_closed()
        except:
            pass

    if hasattr(app, 'dbfactory'):
        try:
            app.dbfactory.close()
        except:
            pass


# async def db_to_request(app, handler):
#     async def middleware_handler(request):
#         setattr(request, 'db', app.db)
#         try:
#             res = await handler(request)
#         except ModelNotFound:
#             raise web.HTTPNotFound()
#         return res
#
#     return middleware_handler


async def setup(app):
    # create connection to the database
    app.on_startup.append(init_db)
    # shutdown db connection on exit
    # app.middlewares.append(db_to_request)


async def shutdown(app):
    if app.get('db_pool'):
        app['db_pool'].close()
        await app['db_pool'].wait_closed()


class DBFn(object):
    def __init__(self, db_wrapper, fn):
        self.db_wrapper = db_wrapper
        self.fn = fn

    def call(self, *args, **kwargs):
        if len(args):
            formatted_args = ','.join(['?' for e in args])
            _args = args
        elif len(kwargs):
            formatted_args = ','.join(['{}:=:{}'.format(k, k) for k in kwargs])
            _args = kwargs
        else:
            formatted_args = ''
            _args = {}

        sql = f"select {self.fn}({formatted_args}) r"
        return self.db_wrapper.first(sql, _args, column='r' )

    def call_rec(self, return_sig, *args, **kwargs):
        if len(args):
            formatted_args = ','.join(['?' for e in args])
            _args = args
        elif len(kwargs):
            formatted_args = ','.join(['{}:=:{}'.format(k, k) for k in kwargs])
            _args = kwargs
        else:
            formatted_args = ''
            _args = {}

        sql = f"select * from {self.fn}({formatted_args}) as {return_sig}"
        return self.db_wrapper.first(sql, _args)

    def __call__(self, *args, **kwargs):
        return self.call(*args, **kwargs)


class DBFnCaller(object):
    def __init__(self, db_wrapper):
        self.db_wrapper = db_wrapper

    def __getattr__(self, item):
        return DBFn(self.db_wrapper, item)


class DBWrapper(object):
    def __init__(self, pool):
        self.pool = pool
        self.fn = DBFnCaller(self)

    def _prepare_sql(self, sql):
        return sql

    def _get_cursor(self, conn):
        return conn.cursor()

    async def await_pool(self):
        if asyncio.iscoroutine(self.pool):
            self.pool = await self.pool
        return self.pool

    async def execute(self, sql, bindings=tuple()):
        await self.await_pool()
        async with self.pool.acquire() as conn:
            async with self._get_cursor(conn) as cur:
                await cur.execute(self._prepare_sql(sql), bindings)

    async def query(self, sql, bindings=tuple()):
        await self.await_pool()
        async with self.pool.acquire() as conn:
            async with self._get_cursor(conn) as cur:
                await cur.execute(self._prepare_sql(sql), bindings)
                r = await cur.fetchall()
                return r if r else []

    async def first(self, sql, bindings=tuple(), column=None):
        await self.await_pool()
        async with self.pool.acquire() as conn:
            async with self._get_cursor(conn) as cur:
                await cur.execute(self._prepare_sql(sql), bindings)
                res = await cur.fetchone()
                if res and column:
                    if type(column) == str:
                        return getattr(res, column)
                    else:
                        return res[column]
                return res

    async def call(self, sql, bindings=tuple(), column=None):
        await self.await_pool()
        async with self.pool.acquire() as conn:
            async with self._get_cursor(conn) as cur:
                await cur.execute(self._prepare_sql(sql), bindings)
                res = await cur.fetchone()
                if res and column:
                    if type(column) == str:
                        return getattr(res, column)
                    else:
                        return res[column]
                return res


class DBPGWrapper(DBWrapper):

    def __init__(self, pool, cursor=None):
        super().__init__(pool)
        self.cursor_type = cursor

    def _get_cursor(self, conn):
        return conn.cursor(cursor_factory=self.cursor_type)

    def _prepare_sql(self, sql):
        return re.sub(':([a-zA-Z_][a-zA-Z_0-9]*)', '%(\\1)s', sql.replace('?', '%s'))
