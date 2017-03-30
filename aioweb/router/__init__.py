import importlib

from aiohttp import hdrs, web
from aiohttp.log import web_logger

from aioweb.router.context import DefaultContext, AuthenticatedContext
from aioweb.util import snake_to_camel, handler_as_coroutine
from .mutidirstatic import StaticMultidirResource


class Router(object):

    def __init__(self, app, name='', prefix='', parent=None, package='app', context=DefaultContext()):
        self.app = app
        self.name = name
        self.prefix = prefix
        self.parent = parent
        self.package = package
        self.view_prefix = ''
        self.context = context
        self.routers = []
        self._currentPrefix = ''
        self._currentName = ''
        self._currentPackage = ''

    # TODO: move to config
    def set_view_prefix(self, prefix):
        self.view_prefix = prefix

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

    def _import_controller(self, name):
        ctrl_class_name = snake_to_camel("%s_controller" % name)

        mod = importlib.import_module("%s.controllers.%s" % (self.package, name))

        ctrl_class = getattr(mod, ctrl_class_name)

        ctrl_class_name = '.'.join((self.package, name))
        if ctrl_class_name not in self.app.controllers:
            self.app.controllers[ctrl_class_name] = ctrl_class(self.app)
            self.app.controllers[ctrl_class_name].search_path = self.view_prefix
        return self.app.controllers[ctrl_class_name]

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
            if self.context.check(request):
                return await handler(action, request)
            else:
                raise web.HTTPForbidden(reason=self.context.reason)

        url = "/%s/%s" % (controller, '' if action == 'index' else '%s/' % action)

        return [url, action_handler, name.replace('#', '.')]

    def _resolve_handler(self, url, handler=None):
        gen_name = None
        if handler is None:
            [url, handler, gen_name] = self._resolve_handler_by_name(url)
        elif type(handler) == str:
            [_, handler, gen_name] = self._resolve_handler_by_name(handler)
        elif callable(handler):
            async def wrapped_handler(request):
                # TODO: custom responses for contexts. For example redirect to login page in AuthContext
                if self.context.check(request):
                    return await handler_as_coroutine(handler)(request)
                else:
                    raise web.HTTPForbidden(reason=self.context.reason)
            handler = wrapped_handler

        return url, handler, gen_name

    def _add_route(self, method, url, handler=None, name=None, **kwargs):
        gen_name = ''
        try:
            [url, handler, gen_name] = self._resolve_handler(url, handler)
            self.app.router.add_route(method, self._get_baseurl(url), handler, name=self._get_namespace(name if name else gen_name),
                                      **kwargs)
        except Exception as e:
            web_logger.warn("invalid route: %s [%s]. skip\nreason: %s" % (url, name if name else gen_name, e))

        self._currentName = self._get_namespace(name if name else gen_name)
        self._currentPrefix = url
        return self


    def head(self, url, handler=None, name=None, **kwargs):
        return self._add_route(hdrs.METH_HEAD, url, handler, name, **kwargs)

    def get(self, url, handler=None, name=None, **kwargs):
        return self._add_route(hdrs.METH_GET, url, handler, name, **kwargs)

    def post(self, url, handler=None, name=None, **kwargs):
        return self._add_route(hdrs.METH_POST, url, handler, name, **kwargs)

    def put(self, url, handler=None, name=None, **kwargs):
        return self._add_route(hdrs.METH_PUT, url, handler, name, **kwargs)

    def patch(self, url, handler=None, name=None, **kwargs):
        return self._add_route(hdrs.METH_PATCH, url, handler, name, **kwargs)

    def delete(self, url, handler=None, name=None, **kwargs):
        return self._add_route(hdrs.METH_DELETE, url, handler, name, **kwargs)

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
            self.app.router.add_patch(self._get_baseurl('%s/{id:[0-9]+}/' % pref), controller.edit, name='%sedit2' % ns)
        if hasattr(controller, 'add_page'):
            self.app.router.add_get(self._get_baseurl('%s/new/' % pref), controller.add_page, name='%sadd_page' % ns)
        if hasattr(controller, 'add'):
            self.app.router.add_post(self._get_baseurl('%s/' % pref), controller.add, name='%sadd' % ns)
        if hasattr(controller, 'delete'):
            self.app.router.add_post(self._get_baseurl('%s/{id:[0-9]+}/delete/' % pref), controller.delete, name='%sdelete' % ns)
            self.app.router.add_delete(self._get_baseurl('%s/{id:[0-9]+}/' % pref), controller.delete, name='%sdelete2' % ns)

        self._currentName = ns
        self._currentPrefix = self._get_baseurl("%s/{id:[0-9]+}/" % pref)
        self._currentPackage = self.package
        return self

    def root(self, handler, name=None, **kwargs):
        return self.get('/', handler, name, **kwargs)

    def proxy(self, url=None, is_action=False, name=None):
        if is_action:
            [url,_,gen_name] = self._resolve_handler(url)
        else:
            gen_name = ''
        self._currentName = self._get_namespace(name if name else gen_name)
        self._currentPrefix = self._get_baseurl(url)
        self._currentPackage = self.package
        return self

    def static(self, prefix, search_paths, *args, **kwargs):
        assert prefix.startswith('/')
        if prefix.endswith('/'):
            prefix = prefix[:-1]
        resource = StaticMultidirResource(prefix, search_paths, *args, **kwargs)
        self.app.router.register_resource(resource)
        return self

    def constrained(self, context=DefaultContext()):
        subrouter = Router(self.app, prefix=self._currentPrefix,
                           name=self._currentName,
                           package=self._currentPackage,
                           context=context)
        self.routers.append(subrouter)
        return subrouter

    def use(self, url, app_name, name=''):
        oldName = self._currentName
        oldPrefix = self._currentPrefix
        oldPackage = self._currentPackage
        self._currentName = name if name else app_name
        self._currentPrefix = url
        self._currentPackage = app_name
        with self as subrouter:
            try:
                mod = importlib.import_module("%s.config.routes" % app_name)
                setup = getattr(mod, 'setup')
                setup(subrouter)
            except AttributeError:
                web_logger.warn("no setup method in %s router" % app_name)
            except ImportError as e:
                web_logger.warn("no routes for app %s" % app_name)

        self._currentName = oldName
        self._currentPrefix = oldPrefix
        self._currentPackage = oldPackage

    def __enter__(self):
        return self.constrained(self.context)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._currentName = ''
        self._currentPrefix = ''
        self._currentPackage = ''

def setup_routes(app):
    from config import routes
    setattr(app, 'controllers', {})

    routes.setup(Router(app))
