from aioweb.conf import settings
import importlib

__backend = importlib.import_module("aioweb.modules.template.backends.%s" % settings.TEMPLATE_BACKEND)

render = getattr(__backend, 'render')
render_string = getattr(__backend, 'render_string')

async def setup(app):
    backend_setup = getattr(__backend, 'setup')

    return await backend_setup(app)

