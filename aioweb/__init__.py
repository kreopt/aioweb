import importlib
import os
import traceback

from aiohttp.log import web_logger, access_logger
from aiohttp.web import Application as AioApp
from aioweb.util import awaitable
from yarl import URL

from aioweb.middleware import setup_middlewares
from aioweb.util.conf_reader import ConfigReader
from .core import router
from .conf import settings


class Application(AioApp):
    last_controller = None

    def __init__(self, *, logger=web_logger, loop=None, router=None, config=ConfigReader('config/config.yml'),
                 debug=...):
        super().__init__(logger=logger, loop=loop, router=router, middlewares=[], debug=debug)
        self.conf = config
        self.modules = set()

    async def setup(self):

        for mod_name in settings.MODULES:
            try:
                mod = importlib.import_module(".modules.%s" % mod_name, __name__)
                setup = getattr(mod, 'setup')
                if setup:
                    self.modules.add(mod_name)
                    await setup(self)
            except (ImportError, AttributeError) as e:
                traceback.print_exc()

        await setup_middlewares(self)
        router.setup_routes(self)

        try:
            mod = importlib.import_module("app")
            setup = getattr(mod, 'setup')
            await awaitable(setup(self))
        except (ImportError, AttributeError) as e:
            pass

    async def shutdown(self):
        for mod_name in settings.MODULES:
            try:
                mod = importlib.import_module(".modules.%s" % mod_name, __name__)
                shutdown = getattr(mod, 'shutdown')
                if shutdown:
                    await shutdown(self)
            except (ImportError, AttributeError) as e:
                pass
        try:
            mod = importlib.import_module("app")
            shutdown = getattr(mod, 'shutdown')
            await awaitable(shutdown(self))
        except (ImportError, AttributeError) as e:
            pass

    def has_module(self, module):
        return module in self.modules

    async def _handle(self, request):
        # data = await request.post()
        # http_method = request.headers.get('X-Http-Method-Override', '').upper()
        # http_method = data.get('X-Http-Method-Override', '').upper()
        overriden = request.clone(method=request.method,
                              rel_url="?".join((request.rel_url.path.rstrip(
                                  '/') if request.rel_url.path != '/' else request.rel_url.path,
                                                request.query_string))
                              )

        return await super()._handle(overriden)


def run_app(app, *,
            shutdown_timeout=60.0, ssl_context=None,
            print=print, backlog=128, access_log_format=None,
            access_log=access_logger, servers=1):
    """Run an app locally"""
    app['env'] = os.environ.get('AIOWEB_ENV', 'development')
    conf = {
        'host': '0.0.0.0',
        'port': 8000
    }
    conf_reader = ConfigReader('config/server.yml')
    conf.update(conf_reader.config.get(app['env']))

    host = conf['host']
    port = conf['port']
    servers = conf.get('servers', 1)
    unix_socket = conf.get('unix')

    if port is None:
        if not ssl_context:
            port = 8000
        else:
            port = 8443

    loop = app.loop

    make_handler_kwargs = dict()
    if access_log_format is not None:
        make_handler_kwargs['access_log_format'] = access_log_format
    handler = app.make_handler(access_log=access_log,
                               **make_handler_kwargs)

    loop.run_until_complete(app.startup())
    if unix_socket:
        sockets = []
        if servers == 1:
            sockets = [unix_socket]
        else:
            path, ext = os.path.splitext(unix_socket)
            for i in range(1, servers + 1):
                sockets.append("{}.{:02d}{}".format(path, i, ext))
        for socket in sockets:
            try:
                os.unlink(socket)
            except:
                pass
            srv = loop.run_until_complete(loop.create_unix_server(handler, path=socket,
                                                                  ssl=ssl_context,
                                                                  backlog=backlog))
            os.chmod(socket, 0o664)
            print("======== Running on unix://{} ========".format(socket))
        print("\n(Press CTRL+C to quit)")

        # try:
        #     os.unlink(unix_socket)
        # except:
        #     pass
        # srv = loop.run_until_complete(loop.create_unix_server(handler, path=unix_socket,
        #                                                       ssl=ssl_context,
        #                                                       backlog=backlog))
        # os.chmod(unix_socket, 0o664)
        # print("======== Running on unix://{} ========\n"
        #       "(Press CTRL+C to quit)".format(unix_socket))
    else:
        srv = loop.run_until_complete(loop.create_server(handler, host,
                                                         port, ssl=ssl_context,
                                                         backlog=backlog))

        scheme = 'https' if ssl_context else 'http'
        url = URL('{}://localhost'.format(scheme))
        url = url.with_host(host).with_port(port)
        print("======== Running on {} ========\n"
              "(Press CTRL+C to quit)".format(url))

    try:
        loop.run_forever()
    except KeyboardInterrupt:  # pragma: no cover
        pass
    finally:
        srv.close()
        loop.run_until_complete(srv.wait_closed())
        loop.run_until_complete(app.shutdown())
        loop.run_until_complete(handler.shutdown(shutdown_timeout))
        loop.run_until_complete(app.cleanup())
    loop.close()


def start_app(app, *,
              shutdown_timeout=60.0,
              ssl_context=None,
              port=None,
              host="0.0.0.0",
              socket=None,
              servers=1,
              log="log/server.log",
              log_level="debug",
              print=print,
              backlog=128,
              access_log_format=None,
              access_log=access_logger):
    loop = app.loop
    app['env'] = os.environ.get('AIOWEB_ENV', 'development')
    if not port:
        port = 8000 if not ssl_context else 8443

    make_handler_kwargs = dict()
    if access_log_format is not None:
        make_handler_kwargs['access_log_format'] = access_log_format
    handler = app.make_handler(access_log=access_log, **make_handler_kwargs)

    loop.run_until_complete(app.startup())
    if socket:
        sockets = []
        if servers == 1:
            sockets = [socket]
        else:
            path, ext = os.path.splitext(socket)
            for i in range(1, servers + 1):
                sockets.append("{}.{:02d}{}".format(path, i, ext))
        for socket in sockets:
            try:
                os.unlink(socket)
            except:
                pass
            srv = loop.run_until_complete(loop.create_unix_server(handler, path=socket,
                                                                  ssl=ssl_context,
                                                                  backlog=backlog))
            os.chmod(socket, 0o664)
            print("======== Running on unix://{} ========".format(socket))
        print("\n(Press CTRL+C to quit)")
    else:
        srv = loop.run_until_complete(loop.create_server(handler, host,
                                                         port, ssl=ssl_context,
                                                         backlog=backlog))

        scheme = 'https' if ssl_context else 'http'
        url = URL('{}://localhost'.format(scheme))
        url = url.with_host(host).with_port(port)
        print("======== Running on {} ========\n"
              "(Press CTRL+C to quit)".format(url))

    try:
        loop.run_forever()
    except KeyboardInterrupt:  # pragma: no cover
        pass
    finally:
        srv.close()
        loop.run_until_complete(srv.wait_closed())
        loop.run_until_complete(handler.shutdown(shutdown_timeout))
        loop.run_until_complete(app.shutdown())
        loop.run_until_complete(app.cleanup())
    loop.close()
