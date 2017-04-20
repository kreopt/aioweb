import os
from enum import Enum

from aiohttp import web
from aiohttp_jinja2 import APP_KEY

from aioweb.render import render_template
from aioweb.util import extract_name_from_class, handler_as_coroutine

def before(before_fn):
    def decorator(fn):
        def decorated(self, *args, **kwargs):
            before_fn(self)
            return fn(self, *args, **kwargs)
        return decorated
    return decorator

class ProcessDescriptor(Enum):
    FN = 'fn'
    ONLY = 'only'
    EXCEPT = 'exclude'

# def before_action(fn):
#     def decorator(Cls):
#         Cls.BEFORE_ACTIONS.insert(0, {
#             ProcessDescriptor.FN
#         })
#         return Cls
#     return decorator

class BaseController(object):
    EMPTY_LAYOUT = 'no_layout.html'

    def __init__(self, request):
        self.app = request.app
        self.request = request
        self.search_path = ''
        self._controller = extract_name_from_class(self.__class__.__name__, 'Controller')
        self._layout = None
        self._template = None
        self._defaultLayout = BaseController.EMPTY_LAYOUT
        self.publicActions = None

    @classmethod
    def before_action(cls, fn, only=tuple(), exclude=tuple()):
        if not hasattr(cls, '__BEFORE_ACTIONS'):
            setattr(cls, '__BEFORE_ACTIONS', [])
        getattr(cls,'__BEFORE_ACTIONS').append({ProcessDescriptor.FN: fn, ProcessDescriptor.ONLY:only, ProcessDescriptor.EXCEPT:exclude})

    def use_layout(self, layout):
        self._layout = layout

    def use_view(self, view):
        self._template = view

    def _render(self, data):
        self.request.app[APP_KEY].globals['controller'] = self
        return render_template(self._template, self.request, data)

    async def _dispatch(self, actionName):

        self._layout = self._defaultLayout if not self.request.is_ajax() else BaseController.EMPTY_LAYOUT
        self._template = os.path.join(self.search_path, self._controller, '%s.html' % actionName)

        try:
            action = getattr(self, actionName)
        except AttributeError as e:
            # TODO:
            raise e

        for beforeAction in getattr(self.__class__, '__BEFORE_ACTIONS', []):
            if actionName not in beforeAction[ProcessDescriptor.EXCEPT] and \
                (actionName in beforeAction[ProcessDescriptor.ONLY] or
                     len(beforeAction[ProcessDescriptor.ONLY]) == 0):
                res = await handler_as_coroutine(beforeAction[ProcessDescriptor.FN])(self)

                if isinstance(res, web.Response):
                    return res

        res = await handler_as_coroutine(action)()

        if isinstance(res, web.Response):
            return res

        accept = self.request.headers['accept']

        if accept.startswith('application/json'):
            return web.json_response(res)

        return self._render(res)
