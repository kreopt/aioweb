import os

from aiohttp import web
from orator import DatabaseManager
from orator.exceptions.orm import ModelNotFound

from . import settings
from aiohttp.log import web_logger

from orator import Model
import yaml

async def init_db(app):
    with open(os.path.join(settings.BASE_DIR, 'config/database.yml'), 'r') as stream:
        conf = yaml.load(stream)
    db_conf = conf.get(conf.get('default', 'development'))
    if not hasattr(app, 'db') and db_conf:
        web_logger.warn("database path: %s" % db_conf['database'])
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
