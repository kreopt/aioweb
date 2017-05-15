import os

from aiohttp import web
from orator import DatabaseManager
from orator.exceptions.orm import ModelNotFound

from aioweb import ConfigReader
from aioweb.conf import settings

from orator import Model


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

    if Model.get_connection_resolver():
        Model.get_connection_resolver().disconnect()
    Model.set_connection_resolver(DatabaseManager(dbconfig))


async def init_db(app):
    db_conf = get_dbconfig()

    if not db_conf:
        raise ReferenceError('Database configuration does not contain databases domain')
    # db_conf = db_conf.get(conf.get('default', 'development'))
    if not hasattr(app, 'db'):
        for db in db_conf.values():
            if isinstance(db, dict) and db.get('driver') == 'sqlite':
                db['database'] = os.path.join(settings.BASE_DIR, 'db', db.get('database', 'db.sqlite3'))
                # web_logger.warn("database path: %s" % db_conf['database'])
        db = DatabaseManager(db_conf)
        Model.set_connection_resolver(db)
        setattr(app, 'db', db)


async def close_db(app):
    if hasattr(app, 'db'):
        try:
            app.db.close()
            app.db.wait_closed()
        except:
            pass


async def db_to_request(app, handler):
    async def middleware_handler(request):
        setattr(request, 'db', app.db)
        try:
            res = await handler(request)
        except ModelNotFound:
            raise web.HTTPNotFound()
        return res

    return middleware_handler


async def setup(app):
    # create connection to the database
    app.on_startup.append(init_db)
    # shutdown db connection on exit
    app.on_cleanup.append(close_db)
    app.middlewares.append(db_to_request)
