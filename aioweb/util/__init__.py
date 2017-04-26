import asyncio
import inspect
import os
import re
import importlib.util

import inflection


def extract_name_from_class(class_name, item_type):
    return inflection.underscore(re.sub('%s$' % item_type, '', class_name))


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
    ctrl_class_name = inflection.camelize("%s_controller" % name)

    mod = importlib.import_module("%s.controllers.%s" % (package if package else 'app', name))

    ctrl_class = getattr(mod, ctrl_class_name)

    ctrl_class_name = '.'.join((package, name))
    return ctrl_class, ctrl_class_name


class PrivateData(object):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        for arg in kwargs:
            setattr(self, arg, kwargs[arg])
