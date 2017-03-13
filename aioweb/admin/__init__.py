import importlib

from aioweb import settings

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
