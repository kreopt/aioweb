from enum import Enum

from aiohttp import web

import aioweb.core.controller
##
## Preprocessing
##
from aioweb.util import get_own_properties


class CtlDecoratorDescriptor(Enum):
    VAL = 'val'
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
        getattr(cls, '__BEFORE_ACTIONS').insert(0, {
            CtlDecoratorDescriptor.VAL: fn,
            CtlDecoratorDescriptor.ONLY: only,
            CtlDecoratorDescriptor.EXCEPT: exclude
        })
        return cls

    return decorate


def cors(hosts, only=tuple(), exclude=tuple()):
    def decorate(cls):
        if not hasattr(cls, '__HEADERS'):
            setattr(cls, '__HEADERS', {})
        getattr(cls, '__HEADERS')['Access-Control-Allow-Origin'] = {
            CtlDecoratorDescriptor.VAL: hosts,
            CtlDecoratorDescriptor.ONLY: only,
            CtlDecoratorDescriptor.EXCEPT: exclude
        }
        return cls

    return decorate


def header(key, value, only=tuple(), exclude=tuple()):
    def decorate(cls):
        if not hasattr(cls, '__HEADERS'):
            setattr(cls, '__HEADERS', {})
        getattr(cls, '__HEADERS')[key] = {
            CtlDecoratorDescriptor.VAL: value,
            CtlDecoratorDescriptor.ONLY: only,
            CtlDecoratorDescriptor.EXCEPT: exclude
        }
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


##
## Router
##

def redirect_on_success(action_name, by_name=None, params=None):
    def decorator(fn):
        async def decorated(self, *args, **kwargs):
            params_data = {}
            if params:
                for param in params:
                    if params[param][0] == 'match':
                        params_data[param] = self.request.match_info[params[param][1]]
            res = await fn(self, *args, **kwargs)
            if not self.request.is_ajax():
                if by_name:
                    return web.HTTPFound(self.router.resolve_named(action_name, params_data))
                else:
                    return web.HTTPFound(self.path_for(action_name, None, params_data))
            return res

        return decorated

    return decorator

##
## Content negotiation
##
def content_type(only=tuple(), exclude=tuple()):
    def decorator(fn):
        setattr(fn, 'content_type', {
            CtlDecoratorDescriptor.EXCEPT: exclude,
            CtlDecoratorDescriptor.ONLY: only
        })
        return fn
    return decorator
