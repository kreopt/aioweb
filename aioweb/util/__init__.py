import asyncio
import inspect
import os
import re
import importlib.util


def camel_to_snake(text):
    import re
    str1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', str1).lower()


def snake_to_camel(text):
    return ''.join(x.capitalize() or '_' for x in text.split('_'))


def extract_name_from_class(class_name, item_type):
    return camel_to_snake(re.sub('%s$' % item_type, '', class_name))


# def as_coroutine(handler):
#     if not asyncio.iscoroutinefunction(handler):
#         return asyncio.coroutine(handler)
#     return handler

async def awaitable(result):
    if asyncio.iscoroutine(result):
        return await result
    return result


def package_path(pkg):
    return os.path.dirname(importlib.util.find_spec(pkg).origin)


def get_own_properties(cls, predicate=inspect.isfunction):
    return [e for e in inspect.getmembers(cls, inspect.isfunction) if e[0] in cls.__dict__]


def import_controller(name, package='app'):
    if type(name) != str:
        raise AssertionError('controller name should be string')
    ctrl_class_name = snake_to_camel("%s_controller" % name)

    mod = importlib.import_module("%s.controllers.%s" % (package, name))

    ctrl_class = getattr(mod, ctrl_class_name)

    ctrl_class_name = '.'.join((package, name))
    return ctrl_class, ctrl_class_name

class PrivateData(object):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        for arg in kwargs:
            setattr(self, arg, kwargs[arg])
