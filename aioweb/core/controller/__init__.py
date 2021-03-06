import os

from aiohttp import web
from aiohttp_session import get_session

from aioweb.core.controller.decorators import CtlDecoratorDescriptor
from aioweb.core.controller.serializers import make_serializer
from aioweb.core.controller.strong_parameters import StrongParameters
from aioweb.modules.session.flash import Flash
from aioweb.util import extract_name_from_class, awaitable, PrivateData


class Controller(object):
    EMPTY_LAYOUT = 'no_layout.html'
    DEFAULT_MIME = 'text/html'

    def __init__(self, request, router):
        self.app = request.app
        if hasattr(self.app, 'db'):
            self.db = self.app.db
        self.request = request
        self._private = PrivateData(
            search_path='',
            controller=extract_name_from_class(self.__class__.__name__, 'Controller'),
            layout=None,
            template=None,
            router=router,
            session=None,
            flash=None,
            headers=[],
            parameters=None,
            query=None
        )
        if not hasattr(self.__class__, 'LAYOUT'):
            setattr(self.__class__, 'LAYOUT', Controller.EMPTY_LAYOUT)

    def path_for(self, action, prefix=None, params={}):
        # if prefix:
        #     return self.app.base_router.resolve_action_url(self._private.controller if prefix is None else prefix, action,
        #                                           **params)
        # else:
        return self.router.resolve_action_url(self._private.controller if prefix is None else prefix, action, **params)

    def url_for(self, action, prefix=None, params={}):
        return "%s://%s%s%s" % (self.request.url.scheme,
                                 self.request.url.host,
                                 ":%s" % self.request.url.port if self.request.url.port != 80 else "",
                                 self.path_for(action, prefix, params=params))

    async def params_typesafe(self, args):
        if self._private.parameters is None:
            self._private.parameters = (await StrongParameters().parse(self.request, parse_body=True)).with_routes(self.request)
        return self._private.parameters.typesafe(args) if args else self._private.parameters

    async def params(self, *args, parse_body=True, require=True):
        if self._private.parameters is None:
            self._private.parameters = (await StrongParameters().parse(self.request, parse_body=parse_body)).with_routes(self.request)
        if require:
            return self._private.parameters.require(*args) if args else self._private.parameters
        else:
            return self._private.parameters.permit(*args) if args else self._private.parameters

    async def query(self, *args):
        if self._private.query is None:
            self._private.query = (await StrongParameters().parse(self.request, parse_body=False)).with_routes(self.request)
        return self._private.query.permit(*args) if args else self._private.query

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

    async def _dispatch(self, action, actionName):

        self._private.layout = getattr(self.__class__,
                                       'LAYOUT') if not self.request.is_ajax() else Controller.EMPTY_LAYOUT
        self._private.template = os.path.join(self._private.search_path, self._private.controller,
                                              '%s.html' % actionName)

        self._private.session = await get_session(self.request)
        self._private.flash = Flash(self._private.session)


        # TODO: something better
        beforeActionRes = {}
        for beforeAction in getattr(self.__class__, '__BEFORE_ACTIONS', []):
            if actionName not in beforeAction[CtlDecoratorDescriptor.EXCEPT] and \
                    (actionName in beforeAction[CtlDecoratorDescriptor.ONLY] or
                             len(beforeAction[CtlDecoratorDescriptor.ONLY]) == 0):
                res = await awaitable(beforeAction[CtlDecoratorDescriptor.VAL](self))

                if isinstance(res, web.Response):
                    return res

                if isinstance(res, dict):
                    beforeActionRes.update(res)

        try:
            res = await awaitable(action())
        except web.HTTPException as e:
            self._private.flash.sync()
            raise e
        except Exception as e:
            self._private.flash.sync()
            raise web.HTTPInternalServerError()

        if isinstance(res, web.Response):
            self._private.flash.sync()
            return res

        if res is None:
            res = {}
        res.update(beforeActionRes)

        response = await self.request.serializer.serialize(res)

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
