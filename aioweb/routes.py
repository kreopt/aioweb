import importlib

from aiohttp import hdrs
from aiohttp.log import web_logger

from aioweb.util import snake_to_camel


class Router(object):

    controllers = {}

    def __init__(self, app, name='', prefix='', parent=None):
        self.app = app
        self.name = name
        self.prefix = prefix
        self.parent = parent
        self.routers = []

    def _get_namespace(self, name=None):
        names = []
        if name:
            names.append(name)
        if self.name:
            names.append(self.name)
        parent = self.parent
        while parent:
            if parent.name:
                names.append(parent.name)
            parent = parent.parent
        names.reverse()
        return ':'.join(names) if len(names) else None

    def _get_baseurl(self, url):
        prefixes = [url]
        if self.prefix:
            prefixes.append(self.prefix)
        parent = self.parent
        while parent:
            if parent.prefix:
                prefixes.append(parent.prefix)
            parent = parent.parent
        prefixes.reverse()
        return '/'.join(prefixes).replace('///', '/').replace('//', '/')

    def use(self, app_name, name='', prefix=''):
        try:
            try:
                mod = importlib.import_module("app.%s.router" % app_name)
            except ImportError as e:
                mod = importlib.import_module("%s.router" % app_name)
            AppRouter = getattr(mod, 'AppRouter')
            router = AppRouter(self.app,
                                          name=name,
                                          prefix=prefix,
                                          parent=self)
            self.routers.append(router)
            router.setup()

        except ImportError as e:
            pass
        except AttributeError:
            pass

    def _import_controller(self, name):
        ctrl_class_name = snake_to_camel("%s_controller" % name)

        mod = importlib.import_module("app.controllers.%s" % name)

        ctrl_class = getattr(mod, ctrl_class_name)

        if ctrl_class_name not in Router.controllers:
            Router.controllers[ctrl_class_name] = ctrl_class(self.app)
        return Router.controllers[ctrl_class_name]

    def _resolve_handler_by_name(self, name):
        try:
            [controller, action] = name.split('#')
        except ValueError as e:
            web_logger.warn("invalid action signature: %s. skip" % name)
            raise e

        try:
            ctrl_inst = self._import_controller(controller)
        except Exception as e:
            web_logger.warn("Failed to import controller: %s. skip\n reason : %s" % (controller, e))
            raise e

        async def action_handler(request):
            handler = getattr(ctrl_inst, '_dispatch')
            return await handler(action, request)

        url = "/%s/%s/" % (controller, action)

        return [url, action_handler]

    def _resolve_handler(self, url, handler=None):
        if handler is None:
            [url, handler] = self._resolve_handler_by_name(url)
        elif type(handler) == str:
            [_, handler] = self._resolve_handler_by_name(handler)
        return url, handler

    def _add_route(self, method, url, handler=None, name=None, **kwargs):
        try:
            [url, handler] = self._resolve_handler(url, handler)
            self.app.router.add_route(method, self._get_baseurl(url), handler, name=self._get_namespace(name),
                                      **kwargs)
        except Exception as e:
            web_logger.warn("invalid route: %s [%s]. skip\nreason: %s" % (url, name if name else '**unnamed**', e))


    def head(self, url, handler=None, name=None, **kwargs):
        self._add_route(hdrs.METH_HEAD, url, handler, name, **kwargs)

    def get(self, url, handler=None, name=None, **kwargs):
        self._add_route(hdrs.METH_GET, url, handler, name, **kwargs)

    def post(self, url, handler=None, name=None, **kwargs):
        self._add_route(hdrs.METH_POST, url, handler, name, **kwargs)

    def put(self, url, handler=None, name=None, **kwargs):
        self._add_route(hdrs.METH_PUT, url, handler, name, **kwargs)

    def patch(self, url, handler=None, name=None, **kwargs):
        self._add_route(hdrs.METH_PATCH, url, handler, name, **kwargs)

    def delete(self, url, handler=None, name=None, **kwargs):
        self._add_route(hdrs.METH_DELETE, url, handler, name, **kwargs)

    def resource(self, res_name, controller, prefix='', name=None, **kwargs):
        ns = self._get_namespace(name)
        if name:
            ns = ':'.join((ns, name)) if ns else name
        else:
            if ns:
                ns = "%s:" % ns

        if type(controller) == str:
            controller = self._import_controller(controller)

        pref = '/'.join((prefix, res_name)).replace('///', '/').replace('//', '/')
        if hasattr(controller, 'index'):
            self.app.router.add_get(self._get_baseurl("%s/" % pref), controller.index, name='%sindex' % ns)
        if hasattr(controller, 'edit_page'):
            self.app.router.add_get(self._get_baseurl("%s/{id:[0-9]+}/" % pref), controller.edit_page, name='%sedit_page' % ns)
        if hasattr(controller, 'edit'):
            self.app.router.add_post(self._get_baseurl('%s/{id:[0-9]+}/' % pref), controller.edit, name='%sedit' % ns)
        if hasattr(controller, 'add_page'):
            self.app.router.add_get(self._get_baseurl('%s/add/' % pref), controller.add_page, name='%sadd_page' % ns)
        if hasattr(controller, 'add'):
            self.app.router.add_post(self._get_baseurl('%s/add/' % pref), controller.add, name='%sadd' % ns)
        if hasattr(controller, 'delete'):
            self.app.router.add_post(self._get_baseurl('%s/delete/' % pref), controller.delete, name='%sdelete' % ns)

    def root(self, handler, name=None, **kwargs):
        return self.get('/', handler, name, **kwargs)

def setup_routes(app):
    from config import routes
    routes.setup(Router(app))
