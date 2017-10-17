import os

import re

# from orator import DatabaseManager

from aioweb import ConfigReader
from aioweb.conf import settings

# from orator import Model as OratorModel

from aioweb.core.model import Model

def get_dbconfig():
    conf = ConfigReader('config/database.yml')
    dbconfig = conf.get('databases')

    environment = os.getenv("AIOWEB_ENV", dbconfig["default"])
    dbconfig["default"] = environment
    if dbconfig[environment]["driver"] == "sqlite":
        dbconfig[environment]["database"] = os.path.join(settings.BASE_DIR,
                                                         "db/{}".format(dbconfig[environment]["database"]))
    return dbconfig


def init_db_engine():
    dbconfig = get_dbconfig()

    # if OratorModel.get_connection_resolver():
    #     OratorModel.get_connection_resolver().disconnect()
    #     OratorModel.set_connection_resolver(DatabaseManager(dbconfig))


async def init_db(app):
    db_conf = get_dbconfig()

    if not db_conf:
        raise ReferenceError('Database configuration does not contain databases domain')
    default_conf = db_conf.get(db_conf.get('default', 'development'))
    if not hasattr(app, 'db'):
        if isinstance(default_conf, dict):
            if default_conf.get('driver') == 'pgsql':
                import aiopg
                import psycopg2.extras
                # dbname=aiopg user=aiopg password=passwd host=127.0.0.1
                host_info = []
                if default_conf.get('host'):
                    host_info.append('host = {}'.format(default_conf.get('host')))
                if default_conf.get('port'):
                    host_info.append('port = {}'.format(default_conf.get('port')))
                app['db_pool'] = await aiopg.create_pool("dbname={} {} user={} password={}".format(
                    default_conf.get('database'),
                    ' '.join(host_info),
                    default_conf.get('user'),
                    default_conf.get('password'),
                ))
                setattr(app, 'db', DBPGWrapper(app['db_pool'], cursor=psycopg2.extras.RealDictCursor))
            elif default_conf.get('driver') == 'sqlite':
                import aioodbc
                app['db_pool'] = await aioodbc.create_pool(dsn="Driver=SQLite3;Database={}".format(
                    os.path.join(settings.BASE_DIR, 'db', default_conf.get('database', 'db.sqlite3'))))
                setattr(app, 'db', DBWrapper(app['db_pool']))
                # web_logger.warn("database path: %s" % db_conf['database'])
        # db = DatabaseManager(db_conf)
        # OratorModel.set_connection_resolver(db)
        if hasattr(app, 'db'):
            setattr(Model,'db', app.db)
        if hasattr(app, 'databases'):
            setattr(Model,'databases', app.databases)
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

        sql = 'select {}({}) r'.format(self.fn, formatted_args)
        return self.db_wrapper.first(sql, _args, column='r')

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

    async def execute(self, sql, bindings=tuple()):
        async with self.pool.acquire() as conn:
            async with self._get_cursor(conn) as cur:
                await cur.execute(self._prepare_sql(sql), bindings)

    async def query(self, sql, bindings=tuple()):
        async with self.pool.acquire() as conn:
            async with self._get_cursor(conn) as cur:
                await cur.execute(self._prepare_sql(sql), bindings)
                r = await cur.fetchall()
                return r if r else []

    async def first(self, sql, bindings=tuple(), column=None):
        async with self.pool.acquire() as conn:
            async with self._get_cursor(conn) as cur:
                await cur.execute(self._prepare_sql(sql), bindings)
                res = await cur.fetchone()
                if res and column:
                    return res[column]
                return res

    async def call(self, sql, bindings=tuple(), column=None):
        async with self.pool.acquire() as conn:
            async with self._get_cursor(conn) as cur:
                await cur.execute(self._prepare_sql(sql), bindings)
                res = await cur.fetchone()
                if column:
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
