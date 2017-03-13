import importlib

from aiohttp import hdrs


class Router(object):
    def __init__(self, app, name='', prefix='', parent=None):
        self.app = app
        self.name = name
        self.prefix = prefix
        self.parent = parent
        self.routers = []

    def _get_namespace(self, name=''):
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
        return ':'.join(names)

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

    def head(self, url, handler, name='', **kwargs):
        self.app.router.add_route(hdrs.METH_HEAD, self._get_baseurl(url), handler, name=self._get_namespace(name), **kwargs)

    def get(self, url, handler, name='', **kwargs):
        self.app.router.add_route(hdrs.METH_GET, self._get_baseurl(url), handler, name=self._get_namespace(name), **kwargs)

    def post(self, url, handler, name='', **kwargs):
        self.app.router.add_route(hdrs.METH_POST, self._get_baseurl(url), handler, name=self._get_namespace(name), **kwargs)

    def put(self, url, handler, name='', **kwargs):
        self.app.router.add_route(hdrs.METH_PUT, self._get_baseurl(url), handler, name=self._get_namespace(name), **kwargs)

    def patch(self, url, handler, name='', **kwargs):
        self.app.router.add_route(hdrs.METH_PATCH, self._get_baseurl(url), handler, name=self._get_namespace(name), **kwargs)

    def delete(self, url, handler, name='', **kwargs):
        self.app.router.add_route(hdrs.METH_DELETE, self._get_baseurl(url), handler, name=self._get_namespace(name), **kwargs)

    def resource(self, res_name, controller, prefix='', name='', **kwargs):
        ns = self._get_namespace(name)
        if name:
            ns = ':'.join((ns, name)) if ns else name
        else:
            if ns:
                ns = "%s:" % ns
        pref = '/'.join((prefix, res_name)).replace('///', '/').replace('//', '/')
        if hasattr(controller, 'list'):
            self.app.router.add_get(self._get_baseurl("%s/" % pref), controller.list, name='%slist' % ns)
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

def setup_routes(app):
    from config import routes
    routes.setup(Router(app))
