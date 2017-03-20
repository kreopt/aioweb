import os
from aiohttp import web
from aiohttp_jinja2 import APP_KEY

from aioweb.render import render_template
from aioweb.util import extract_name_from_class, handler_as_coroutine


class BaseController(object):
    EMPTY_LAYOUT = 'no_layout.html'

    def __init__(self, app):
        self.app = app
        self._controller = extract_name_from_class(self.__class__.__name__, 'Controller')
        self._layout = None
        self._template = None
        self._defaultLayout = BaseController.EMPTY_LAYOUT

    def use_layout(self, layout):
        self._layout = layout

    def use_view(self, view):
        self._template = view

    def _render(self, data):
        self.request.app[APP_KEY].globals['controller'] = self
        return render_template(self._template, self.request, data)

    async def _dispatch(self, action, request):
        self.request = request
        self._layout = self._defaultLayout if not request.is_ajax() else BaseController.EMPTY_LAYOUT
        self._template = os.path.join(self._controller, '%s.html' % action)

        try:
            action = getattr(self, action)
        except AttributeError as e:
            # TODO:
            raise e

        res = await handler_as_coroutine(action)(request)

        if isinstance(res, web.Response):
            return res

        accept = request.headers['accept']

        if accept.startswith('application/json'):
            return web.json_response(res)

        return self._render(res)
