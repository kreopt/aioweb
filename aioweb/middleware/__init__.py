import importlib

from aiohttp.log import web_logger

from .is_ajax import middleware as is_ajax
from .csrf import middleware as csrf_token, setup as csrf_setup, pre_dispatch as csrf_pre_dispatch

from aioweb.conf import settings

PRE_DISPATCHERS = []

def setup_middlewares(app):
    app.middlewares.append(is_ajax)
    app.middlewares.append(csrf_token)
    csrf_setup(app)
    PRE_DISPATCHERS.append(csrf_pre_dispatch)

    for middleware in settings.MIDDLEWARES:
        try:
            mod = importlib.import_module(middleware)
            try:
                mw = getattr(mod, 'middleware')
                app.middlewares.append(mw)
            except AttributeError:
                pass
            try:
                setup = getattr(mod, 'setup')
                setup(app)
            except AttributeError:
                pass
            try:
                PRE_DISPATCHERS.append(getattr(mod, 'pre_dispatch'))
            except AttributeError:
                pass
        except ImportError as e:
            web_logger.warn('Failed to register middleware %s' % middleware)
