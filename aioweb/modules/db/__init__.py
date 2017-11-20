import asyncio
import os

import re

# from orator import DatabaseManager
import typing

import simplejson

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
    def __init__(self, config, loop=None):
        self.config = config
        self.pools = {}
        self.loop = loop

    def connection(self, connection=None):
        if connection is None:
            connection = self.config.get('default', 'development')

        if connection in self.pools:
            return self.pools[connection]

        db_config = self.config[connection]
        dbwrapper = None

        if db_config.get('driver') == 'pgsql':
            # import aiopg
            import asyncpg
            from . import pg_extras
            # dbname=aiopg user=aiopg password=passwd host=127.0.0.1
            host_info = []
            if db_config.get('host'):
                host_info.append('host = {}'.format(db_config.get('host')))
            if db_config.get('port'):
                host_info.append('port = {}'.format(db_config.get('port')))
            pool = asyncpg.create_pool(
                loop=self.loop,
                host=db_config.get('host'),
                port=db_config.get('port'),
                database=db_config.get('database'),
                user=db_config.get('user'),
                password=db_config.get('password'),
            )

            dbwrapper = DBPGWrapper(pool)
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
        setattr(app, 'db', DBConnection(DBFactory(db_conf, loop=app.loop)))
        setattr(Model, 'db', app.db)
        # setattr(app, 'db', db)


async def close_db(app):
    if hasattr(app, 'db'):
        try:
            app.db.close()
            await app.db.wait_closed()
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
    # app.on_startup.append(init_db)
    # app.on_shutdown.append(close_db)
    # shutdown db connection on exit
    # app.middlewares.append(db_to_request)
    pass


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

    def call_json(self, *args, **kwargs):
        if len(args):
            formatted_args = ','.join(['?' for e in args])
            _args = args
        elif len(kwargs):
            formatted_args = ','.join(['{}:=:{}'.format(k, k) for k in kwargs])
            _args = kwargs
        else:
            formatted_args = ''
            _args = {}

        sql = f"select to_jsonb({self.fn}({formatted_args})) r"
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

    def _prepare_sql(self, sql, bindings=None):
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

    def __init__(self, pool):
        super().__init__(pool)

    async def await_pool(self):
        # if asyncio.iscoroutine(self.pool):
        #     self.pool = \
        await self.pool
        return self.pool

    async def _set_type_conversion(self, conn):
        def _encoder(value):
            return simplejson.dumps(value)

        def _decoder(value):
            return simplejson.loads(value)

        await conn.set_type_codec(
            'json', encoder=_encoder, decoder=_decoder, schema='pg_catalog'
        )
        await conn.set_type_codec(
            'jsonb', encoder=_encoder, decoder=_decoder, schema='pg_catalog'
        )

    async def execute(self, sql, bindings=tuple()):
        await self.await_pool()
        async with self.pool.acquire() as conn:
            await self._set_type_conversion(conn)
            await conn.execute(*self._prepare_sql(sql, bindings))

    async def query(self, sql, bindings=tuple()):
        await self.await_pool()
        async with self.pool.acquire() as conn:
            await self._set_type_conversion(conn)
            r = await conn.fetch(*self._prepare_sql(sql, bindings))
            return r if r else []

    async def first(self, sql, bindings=tuple(), column=None):
        await self.await_pool()
        async with self.pool.acquire() as conn:
            await self._set_type_conversion(conn)
            if type(column) == int:
                res = await conn.fetchval(*self._prepare_sql(sql, bindings), column=column)
            else:
                res = await conn.fetchrow(*self._prepare_sql(sql, bindings))
                if res and column and column in res:
                    return res[column]
            return res

    def call(self, sql, bindings=tuple(), column=None):
        return self.first(sql, bindings, column=column)

    def _prepare_sql(self, sql, bindings: typing.Union[tuple, dict]=tuple()):
        if type(bindings) == dict:
            new_bindings = []
            last_sql = sql
            i = 1
            for k in sorted(bindings.keys()):
                sql = sql.replace(f':{k}', f'${i}')
                if last_sql != sql:
                    i += 1
                    new_bindings.append(bindings[k])
                    last_sql = sql
        else:
            new_bindings = bindings
        return [sql, *new_bindings]


    def _flatten_bindings(self, bindings):
        if type(bindings) == dict:
            return [bindings[k] for k in sorted(bindings.keys())]
        return bindings
