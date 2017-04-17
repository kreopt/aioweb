import importlib

from aiohttp.log import web_logger

from aioweb.middleware.is_ajax import middleware as is_ajax
from aioweb.middleware.csrf_token import middleware as csrf_token

from aioweb.conf import settings

def setup_middlewares(app):
    app.middlewares.append(is_ajax)
    app.middlewares.append(csrf_token)

    for middleware in settings.MIDDLEWARES:
        try:
            mod = importlib.import_module(middleware)
            mw = getattr(mod, 'middleware')
            app.middlewares.append(mw)
        except ImportError as e:
            web_logger.warn('Failed to register middleware %s' % middleware)
