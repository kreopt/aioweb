import importlib
import os
from pathlib import Path, PurePath

import jinja2
from collections import Mapping

from aiohttp import web

from aioweb.util import awaitable

from aioweb.conf import settings

from .django_tags import DjangoStatic, DjangoLoad, DjangoUrl, DjangoTrans, DjangoNow

APP_CONTEXT_PROCESSORS_KEY = 'aioweb_jinja2_context_processors'
APP_KEY = 'aioweb_jinja2_environment'
REQUEST_CONTEXT_KEY = 'aioweb_jinja2_context'

@web.middleware
async def context_processors_middleware(request, handler):
    request[REQUEST_CONTEXT_KEY] = {}
    for processor in request.app[APP_CONTEXT_PROCESSORS_KEY]:
        request[REQUEST_CONTEXT_KEY].update(await processor(request))
    return await handler(request)


async def request_processor(request):
    return {'request': request}


class TemplateError(Exception):

    def __init__(self, reason='', text='') -> None:
        self.reason = reason
        self.text = text
        super().__init__()


def render_string(template_name, request, context, *, app_key=APP_KEY):
    env = request.app.get(app_key)
    if env is None:
        text = ("Template engine is not initialized, "
                "call aiohttp_jinja2.setup(..., app_key={}) first"
                "".format(app_key))
        # in order to see meaningful exception message both: on console
        # output and rendered page we add same message to *reason* and
        # *text* arguments.
        raise TemplateError(reason=text, text=text)
    try:
        template = env.get_template(template_name)
    except jinja2.TemplateNotFound as e:
        text = "Template '{}' not found".format(template_name)
        raise TemplateError(reason=text, text=text) from e
    if not isinstance(context, Mapping):
        text = "context should be mapping, not {}".format(type(context))
        # same reason as above
        raise TemplateError(reason=text, text=text)
    if request.get(REQUEST_CONTEXT_KEY):
        context = dict(request[REQUEST_CONTEXT_KEY], **context)
    return template.render_async(context)


async def render(template_name, request, context, *,
                 app_key=APP_KEY, encoding='utf-8', status=200):
    response = web.Response(status=status)
    if context is None:
        context = {}
    text = await render_string(template_name, request, context, app_key=app_key)
    response.content_type = 'text/html'
    response.charset = encoding
    response.text = text
    return response


def get_env(app):
    return app[APP_KEY]


async def setup(app):
    procs = [request_processor]
    # setup Jinja2 template renderer
    app_loaders = [
        # jinja2.FileSystemLoader(os.path.join(settings.BASE_DIR, "app/views_min/")),
        # jinja2.FileSystemLoader(os.path.join(settings.BASE_DIR, "app/views/")),
        # jinja2.PackageLoader("aioweb", "views/")
    ]
    backend_dir = Path(os.path.join(settings.BASE_DIR, 'backends'))
    if backend_dir.is_dir():
        for backend in backend_dir.iterdir():
            if backend.is_dir():
                app_loaders.append(jinja2.FileSystemLoader(str(backend / Path("views/"))))

    env = jinja2.Environment(
        loader=jinja2.ChoiceLoader(app_loaders),
        enable_async=True,
        trim_blocks=True,
        lstrip_blocks=True,
        extensions=[
            DjangoStatic,
            DjangoUrl,
            DjangoNow,
            DjangoTrans
        ])

    env.globals['settings'] = settings
    env.globals['app'] = app

    app[APP_KEY] = env
    app[APP_CONTEXT_PROCESSORS_KEY] = procs
    app.middlewares.append(context_processors_middleware)

    try:
        mod = importlib.import_module("app")
        setup = getattr(mod, 'setup_template')
        await awaitable(setup(env))
    except (ImportError, AttributeError) as e:
        pass
