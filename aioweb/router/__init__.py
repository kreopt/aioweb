import importlib

from aiohttp import hdrs, web
from aiohttp.log import web_logger

from aioweb.router.context import DefaultContext, AuthenticatedContext
from aioweb.util import snake_to_camel, extract_name_from_class, handler_as_coroutine
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
        url = '/'.join(prefixes).replace('///', '/').replace('//', '/')
        if url.endswith('/'):
            url=url[:-1]
        return url

    def _import_controller(self, name):
        if type(name) != str:
            return name
        ctrl_class_name = snake_to_camel("%s_controller" % name)

        mod = importlib.import_module("%s.controllers.%s" % (self.package, name))

        ctrl_class = getattr(mod, ctrl_class_name)

        ctrl_class_name = '.'.join((self.package, name))
        if ctrl_class_name not in self.app.controllers:
            self.app.controllers[ctrl_class_name] = ctrl_class
            self.app.controllers[ctrl_class_name].search_path = self.view_prefix
        return self.app.controllers[ctrl_class_name]

    def _resolve_action(self, controller, action_name):

        if type(controller) == str:
            try:
                ctrl_class = self._import_controller(controller)
            except Exception as e:
                web_logger.warn("Failed to import controller: %s. skip\n reason : %s" % (controller, e))
                raise e
        else:
            ctrl_class = controller

        async def action_handler(request):
            ctrl_instance = ctrl_class(request)
            if self.context.check(request):
                return await ctrl_instance._dispatch(action_name)
            else:
                raise web.HTTPForbidden(reason=self.context.reason)

        url = "/%s/%s" % (controller, '' if action_name == 'index' else '%s/' % action_name)

        return [url, action_handler,
                "%s.%s" % (extract_name_from_class(ctrl_class.__name__, 'Controller'), action_name)]

    def _resolve_handler_by_name(self, name):
        try:
            [controller, action] = name.split('#')
        except ValueError as e:
            web_logger.warn("invalid action signature: %s. skip" % name)
            raise e
        return self._resolve_action(controller, action)

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

        pref = '/'.join((prefix, res_name)).replace('///', '/').replace('//', '/')
        controller = self._import_controller(controller)
        if hasattr(controller, 'index'):
            [url, handler, gen_name] = self._resolve_action(controller, 'index')
            name = "%s.index" % (name if name else gen_name)
            self._add_route(hdrs.METH_GET, self._get_baseurl("%s/" % pref),
                            handler, name=name)
        if hasattr(controller, 'edit_page'):
            [url, handler, gen_name] = self._resolve_action(controller, 'edit_page')
            name = "%s.edit_page" % (name if name else gen_name)
            self._add_route(hdrs.METH_GET, self._get_baseurl("%s/{id:[0-9]+}/" % pref), handler, name=name)
        if hasattr(controller, 'edit'):
            [url, handler, gen_name] = self._resolve_action(controller, 'edit')
            name = "%s.edit" % (name if name else gen_name)
            self._add_route(hdrs.METH_PATCH, self._get_baseurl('%s/{id:[0-9]+}/' % pref), handler, name=name)
        if hasattr(controller, 'add_page'):
            [url, handler, gen_name] = self._resolve_action(controller, 'add_page')
            name = "%s.add_page" % (name if name else gen_name)
            self._add_route(hdrs.METH_GET, self._get_baseurl('%s/add/' % pref), handler, name=name)
        if hasattr(controller, 'add'):
            [url, handler, gen_name] = self._resolve_action(controller, 'add')
            name = "%s.add" % (name if name else gen_name)
            self._add_route(hdrs.METH_POST, self._get_baseurl('%s/add/' % pref), handler, name=name)
        if hasattr(controller, 'delete'):
            [url, handler, gen_name] = self._resolve_action(controller, 'delete')
            name = "%s.delete" % (name if name else gen_name)
            self._add_route(hdrs.METH_DELETE, self._get_baseurl('%s/delete/' % pref), handler, name=name)

        self._currentName = name
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
