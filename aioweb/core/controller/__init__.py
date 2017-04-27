import os

from aiohttp import web
from aiohttp_jinja2 import APP_KEY
from aiohttp_session import get_session

from aioweb.core.controller.decorators import ProcessDescriptor
from aioweb.modules import template
from aioweb.modules.session.flash import Flash
from aioweb.util import extract_name_from_class, awaitable, PrivateData


class Controller(object):
    EMPTY_LAYOUT = 'no_layout.html'

    def __init__(self, request, router):
        self.app = request.app
        self.request = request
        self._private = PrivateData(
            search_path='',
            controller=extract_name_from_class(self.__class__.__name__, 'Controller'),
            layout=None,
            template=None,
            router=router,
            session=None,
            flash=None
        )
        if not hasattr(self.__class__, 'LAYOUT'):
            setattr(self.__class__, 'LAYOUT', Controller.EMPTY_LAYOUT)

    def url_for(self, action):
        return self.router.resolve_action(self._private.controller, action)[0]

    @property
    def session(self):
        return self._private.session

    @property
    def flash(self):
        return self._private.flash

    @property
    def router(self):
        return self._private.router

    @property
    def layout(self):
        return self._private.layout

    @layout.setter
    def layout(self, layout):
        self._private.layout = layout

    @property
    def template(self):
        return self._private.template

    @template.setter
    def template(self, view):
        self._private.template = view

    def render(self, data):
        self.request.app[APP_KEY].globals['controller'] = self
        return template.render(self._private.template, self.request, data)

    async def _dispatch(self, action, actionName):

        self._private.layout = getattr(self.__class__,
                                       'LAYOUT') if not self.request.is_ajax() else Controller.EMPTY_LAYOUT
        self._private.template = os.path.join(self._private.search_path, self._private.controller,
                                              '%s.html' % actionName)

        self._private.session = await get_session(self.request)
        self._private.flash = Flash(self._private.session)

        # TODO: something better
        for beforeAction in getattr(self.__class__, '__BEFORE_ACTIONS', []):
            if actionName not in beforeAction[ProcessDescriptor.EXCEPT] and \
                    (actionName in beforeAction[ProcessDescriptor.ONLY] or
                             len(beforeAction[ProcessDescriptor.ONLY]) == 0):
                res = await awaitable(beforeAction[ProcessDescriptor.FN](self))

                if isinstance(res, web.Response):
                    return res

        try:
            res = await awaitable(action())
        except Exception as e:
            self._private.flash.sync()
            raise e


        if isinstance(res, web.Response):
            self._private.flash.sync()
            return res

        if res is None:
            res = {}

        accept = self.request.headers['accept']

        if accept.startswith('application/json'):
            self._private.flash.sync()
            return web.json_response(res)

        response = self.render(res)

        self._private.flash.sync()
        return response
