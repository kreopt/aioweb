import importlib

from aiohttp import hdrs
from aiohttp.log import web_logger

from aioweb.util import snake_to_camel, extract_name_from_class
from .mutidirstatic import StaticMultidirResource

class Router(object):

    def __init__(self, app, name='', prefix='', parent=None):
        self.app = app
        self.name = name
        self.prefix = prefix
        self.parent = parent
        self.routers = []
        self._currentPrefix = ''
        self._currentName = ''

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
        if type(name) != str:
            return name
        ctrl_class_name = snake_to_camel("%s_controller" % name)

        mod = importlib.import_module("app.controllers.%s" % name)

        ctrl_class = getattr(mod, ctrl_class_name)

        if ctrl_class_name not in self.app.controllers:
            self.app.controllers[ctrl_class_name] = ctrl_class(self.app)
        return self.app.controllers[ctrl_class_name]

    def _resolve_action(self, controller, action_name):

        if type(controller) == str:
            try:
                ctrl_inst = self._import_controller(controller)
            except Exception as e:
                web_logger.warn("Failed to import controller: %s. skip\n reason : %s" % (controller, e))
                raise e
        else:
            ctrl_inst = controller

        async def action_handler(request):
            handler = getattr(ctrl_inst, '_dispatch')
            return await handler(action_name, request)

        url = "/%s/%s" % (controller, '' if action_name == 'index' else '%s/' % action_name)

        return [url, action_handler,
                "%s.%s" % (extract_name_from_class(ctrl_inst.__class__.__name__, 'Controller'), action_name)]

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

    # def _define_resource_action(self, prefix):
    #     pass
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
        return self

    def static(self, prefix, search_paths, *args, **kwargs):
        assert prefix.startswith('/')
        if prefix.endswith('/'):
            prefix = prefix[:-1]
        resource = StaticMultidirResource(prefix, search_paths, *args, **kwargs)
        self.app.router._reg_resource(resource)
        return self

    def __enter__(self):
        subrouter = Router(self.app, prefix=self._currentPrefix, name=self._currentName)
        self.routers.append(subrouter)
        return subrouter

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._currentName = ''
        self._currentPrefix = ''

def setup_routes(app):
    from config import routes
    setattr(app, 'controllers', {})

    def _import_controller(self, name):
        ctrl_class_name = snake_to_camel("%s_controller" % name)

        mod = importlib.import_module("app.controllers.%s" % name)

        ctrl_class = getattr(mod, ctrl_class_name)

        if ctrl_class_name not in self.controllers:
            self.controllers[ctrl_class_name] = ctrl_class(self)
        return self.controllers[ctrl_class_name]

    setattr(app, 'get_controller', _import_controller)

    routes.setup(Router(app))
