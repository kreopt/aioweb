import os

from aiohttp import web
from aiohttp_jinja2 import APP_KEY
from aiohttp_session import get_session

from aioweb.core.controller.decorators import CtlDecoratorDescriptor
from aioweb.core.controller.strong_parameters import StrongParameters
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
            flash=None,
            headers=[]
        )
        if not hasattr(self.__class__, 'LAYOUT'):
            setattr(self.__class__, 'LAYOUT', Controller.EMPTY_LAYOUT)

    def path_for(self, action, prefix=None):
        return self.router.resolve_action_url(self._private.controller if prefix is None else prefix, action)

    def url_for(self, action, prefix=None):
        return "%s://%s%s%s" % (self.request.url.scheme,
                                 self.request.url.host,
                                 ":%s" % self.request.url.port if self.request.url.port != 80 else "",
                                 self.path_for(action, prefix))

    async def params(self):
        return await StrongParameters().parse(self.request)

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
        beforeActionRes = {}
        for corsDomain in getattr(self.__class__, '__BEFORE_ACTIONS', []):
            if actionName not in corsDomain[CtlDecoratorDescriptor.EXCEPT] and \
                    (actionName in corsDomain[CtlDecoratorDescriptor.ONLY] or
                             len(corsDomain[CtlDecoratorDescriptor.ONLY]) == 0):
                res = await awaitable(corsDomain[CtlDecoratorDescriptor.VAL](self))

                if isinstance(res, web.Response):
                    return res

                if isinstance(res, dict):
                    beforeActionRes.update(res)

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
        res.update(beforeActionRes)

        accept = self.request.headers['accept']

        if accept.startswith('application/json'):
            response = web.json_response(res)
        else:
            response = self.render(res)

        # if self._private.headers:
        #     for header in self._private.headers:
        #         response.headers[header] = self._private.headers[header]

        try:
            headers = getattr(self.__class__, '__HEADERS')
            for name in headers:
                descriptior = headers[name]
                if actionName not in descriptior[CtlDecoratorDescriptor.EXCEPT] and \
                        (actionName in descriptior[CtlDecoratorDescriptor.ONLY] or
                                 len(descriptior[CtlDecoratorDescriptor.ONLY]) == 0):
                    response.headers[name] = descriptior[CtlDecoratorDescriptor.VAL]
        except AttributeError:
            pass

        self._private.flash.sync()
        return response
