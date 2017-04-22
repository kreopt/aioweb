import importlib

from aioweb import settings

async def setup(app):
    try:
        importlib.import_module("app.config.admin")
    except ImportError:
        pass
    for appName in settings.APPS:
        try:
            importlib.import_module("%s.config.admin" % appName)
        except ImportError:
            pass


MODELS = {}


class DefaultAdmin(object):
    __id_field__ = 'id'


def register_model(model, admin=DefaultAdmin):
    if not hasattr(admin, '__id_field__'):
        setattr(admin, '__id_field__', 'id')
    MODELS[model.__name__.lower()] = [model, admin]