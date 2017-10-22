import importlib

from aiohttp.log import web_logger
from aiohttp.web_middlewares import normalize_path_middleware

from aioweb.util import awaitable
from .is_ajax import is_ajax_middleware
from .csrf import csrf_middleware, setup as csrf_setup, pre_dispatch as csrf_pre_dispatch

from aioweb.conf import settings

PRE_DISPATCHERS = []


async def setup_middlewares(app):
    app.middlewares.append(normalize_path_middleware(append_slash=True))
    app.middlewares.append(is_ajax_middleware)
    if 'session' in app.modules:
        app.middlewares.append(csrf_middleware)
    csrf_setup(app)
    PRE_DISPATCHERS.append(csrf_pre_dispatch)

    for middleware in settings.MIDDLEWARES:
        try:
            mw_parts = middleware.split(':')
            mod = importlib.import_module(mw_parts[0])
            try:
                mw = getattr(mod, 'middleware' if len(mw_parts) == 1 else mw_parts[1])
                app.middlewares.append(mw)
            except AttributeError:
                pass
            try:
                setup = getattr(mod, 'setup')
                await awaitable(setup(app))
            except AttributeError:
                pass
            try:
                PRE_DISPATCHERS.append(getattr(mod, 'pre_dispatch'))
            except AttributeError:
                pass
        except ImportError as e:
            web_logger.warn('Failed to register middleware %s' % middleware)
