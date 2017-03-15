import os
from aiohttp import web

from aioweb.render import render_template
from aioweb.util import extract_name_from_class, handler_as_coroutine


class BaseController(object):
    def __init__(self, app):
        self.app = app
        self._controller = extract_name_from_class(self.__class__.__name__, 'Controller')
        self._layout = None
        self._template = None

    def use_layout(self, layout):
        self._layout = layout

    def use_view(self, view):
        self._template = view

    def _render(self, data):
        if self._layout:
            return render_template(self._layout, self.request, {'tpl': self._template, 'data': data})
        else:
            return render_template(self._template, self.request, data)

    async def _dispatch(self, action, request):
        self.request = request
        self._layout = None
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

        if accept.startswith('text/html'):
            return self._render(res)
        elif accept.startswith('application/json'):
            return web.json_response(res)
