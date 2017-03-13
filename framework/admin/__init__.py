import importlib

from aiohttp import web

from framework import settings

# subapp = web.Application()

async def setup(app):
    for appName in settings.APPS:
        try:
            mod = importlib.import_module("app.%s.admin" % appName)
        except ImportError:
            pass
        try:
            mod = importlib.import_module("%s.admin" % appName)
        except ImportError:
            pass
