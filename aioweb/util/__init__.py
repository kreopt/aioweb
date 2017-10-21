import asyncio
import importlib
import inspect
import os
import re
import importlib.util

import inflection


def extract_name_from_class(class_name, item_type):
    return inflection.underscore(re.sub('%s$' % item_type, '', class_name))


def awaitable(result):
    if asyncio.iscoroutine(result):
        return result
    f = asyncio.Future()
    f.set_result(result)
    return f


def package_path(pkg):
    return os.path.dirname(importlib.util.find_spec(pkg).origin)


def get_own_properties(cls, predicate=inspect.isfunction):
    return [e for e in inspect.getmembers(cls, inspect.isfunction) if e[0] in cls.__dict__]


def import_controller(name, package=None):
    if type(name) != str:
        raise AssertionError('controller name should be string')
    ctrl_class_name = inflection.camelize("%s_controller" % name)

    mod = importlib.import_module(f"""{f"{package}" if package else ""}.controllers.{name}""")

    ctrl_class = getattr(mod, ctrl_class_name)

    if package:
        ctrl_class_name = '.'.join((package, name))
    return ctrl_class, ctrl_class_name


class PrivateData(object):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        for arg in kwargs:
            setattr(self, arg, kwargs[arg])


class Injector(object):
    def __init__(self, app, class_name, package=None):
        self.imported = {}
        self.app = app
        self.class_name = class_name
        self.format_string = f"{'.' if package else ''}{inflection.pluralize(self.class_name.lower())}.{{name}}"
        self.package = package

    def inject(self, name):
        inject_class = self.imported.get(name)
        if not inject_class:
            mod = importlib.import_module(self.format_string.format(name=name), package=self.package)
            inject_class = getattr(mod, inflection.camelize(f'{name.lower()}_{self.class_name}'))
            self.imported[name] = inject_class

        return inject_class(self.app)

    def __getattr__(self, item):
        return self.inject(item)
