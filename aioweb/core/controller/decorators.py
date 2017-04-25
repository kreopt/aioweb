from enum import Enum

import aioweb.core.controller
##
## Preprocessing
##
from aioweb.util import get_own_properties


class ProcessDescriptor(Enum):
    FN = 'fn'
    ONLY = 'only'
    EXCEPT = 'exclude'

def before(before_fn):
    def decorator(fn):
        def decorated(self, *args, **kwargs):
            before_fn(self)
            return fn(self, *args, **kwargs)
        return decorated
    return decorator


def before_action(fn, only=tuple(), exclude=tuple()):
    def decorate(cls):
        if not hasattr(cls, '__BEFORE_ACTIONS'):
            setattr(cls, '__BEFORE_ACTIONS', [])
        for name, member in get_own_properties(cls):
            if name not in exclude and (name in only or len(only) == 0):
                # setattr(cls, name, before(fn)(member))
                getattr(cls, '__BEFORE_ACTIONS').insert(0,
                    {ProcessDescriptor.FN: fn, ProcessDescriptor.ONLY: only, ProcessDescriptor.EXCEPT: exclude})
        return cls
    return decorate

##
## Render
##

def default_layout(layout_name):
    def decorate(cls):
        setattr(cls, 'LAYOUT', layout_name)
        return cls
    return decorate


def template(template_name):
    def decorator(fn):
        def decorated(self, *args, **kwargs):
            aioweb.core.controller.Controller.template.fset(self, template_name)
            return fn(self, *args, **kwargs)
        return decorated
    return decorator

def layout(template_name):
    def decorator(fn):
        def decorated(self, *args, **kwargs):
            aioweb.core.controller.Controller.template.fset(self, template_name)
            return fn(self, *args, **kwargs)
        return decorated
    return decorator

