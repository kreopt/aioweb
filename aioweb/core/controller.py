import os
from aiohttp import web
from aiohttp_jinja2 import APP_KEY

from aioweb.render import render_template
from aioweb.util import extract_name_from_class, handler_as_coroutine


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

    def use_layout(self, layout):
        self._layout = layout

    def use_view(self, view):
        self._template = view

    async def before_action(self):
        return {}

    def _render(self, data):
        self.request.app[APP_KEY].globals['controller'] = self
        return render_template(self._template, self.request, data)

    async def _dispatch(self, action):

        self._layout = self._defaultLayout if not self.request.is_ajax() else BaseController.EMPTY_LAYOUT
        self._template = os.path.join(self.search_path, self._controller, '%s.html' % action)

        try:
            action = getattr(self, action)
        except AttributeError as e:
            # TODO:
            raise e

        ctx = await handler_as_coroutine(self.before_action)()

        if isinstance(ctx, web.Response):
            return ctx

        res = await handler_as_coroutine(action)()

        if isinstance(res, web.Response):
            return res

        res.update(ctx)

        accept = self.request.headers['accept']

        if accept.startswith('application/json'):
            return web.json_response(res)

        return self._render(res)
