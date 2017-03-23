import importlib

from aiohttp.log import web_logger

from aioweb.middleware.method_override import middleware as method_override
from aioweb.middleware.is_ajax import middleware as is_ajax

from aioweb.conf import settings

def setup_middlewares(app):
    app.middlewares.append(method_override)
    app.middlewares.append(is_ajax)

    for middleware in settings.MIDDLEWARES:
        try:
            mod = importlib.import_module(middleware)
            mw = getattr(mod, 'middleware')
            app.middlewares.append(mw)
        except ImportError as e:
            web_logger.warn('Failed to register middleware %s' % middleware)
