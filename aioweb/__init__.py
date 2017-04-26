import importlib
import os
import traceback

from aiohttp.log import web_logger, access_logger
from aiohttp.web import Application as AioApp
from yarl import URL

from aioweb.middleware import setup_middlewares
from aioweb.util.conf_reader import ConfigReader
from .core import router
from .conf import settings

class Application(AioApp):
    def __init__(self, *, logger=web_logger, loop=None, router=None, config=ConfigReader('config/config.yml'), debug=...):
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

    def has_module(self, module):
        return module in self.modules


    async def _handle(self, request):
        http_method = request.headers.get('X-Http-Method-Override', '').upper()
        overriden = request.clone(method=http_method if http_method else request.method,
                                  rel_url=request.rel_url.path.rstrip('/') if request.rel_url.path != '/' else request.rel_url.path
                                  )

        return await super()._handle(overriden)


def run_app(app, *,
            shutdown_timeout=60.0, ssl_context=None,
            print=print, backlog=128, access_log_format=None,
            access_log=access_logger):
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
        try:
            os.unlink(unix_socket)
        except:pass
        srv = loop.run_until_complete(loop.create_unix_server(handler, path=unix_socket,
                                                                ssl=ssl_context,
                                                                backlog=backlog))
        os.chmod(unix_socket, 0o664)
        print("======== Running on unix://{} ========\n"
              "(Press CTRL+C to quit)".format(unix_socket))
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

