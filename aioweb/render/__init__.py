import asyncio
import functools
import os

import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp.abc import AbstractView
from aiohttp_jinja2 import template as template, render_string, render_template

from aioweb import settings
from .django_tags import DjangoStatic, DjangoLoad, DjangoCsrf, DjangoUrl, DjangoTrans


def json_response(encoding='utf-8'):
    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(*args):
            if asyncio.iscoroutinefunction(func):
                coro = func
            else:
                coro = asyncio.coroutine(func)

            try:
                context = await coro(*args)
                status = 200
            except web.HTTPException as e:
                status = e.status_code
                context = {'error': e.text}

            if isinstance(context, web.StreamResponse):
                return context

            # Supports class based views see web.View
            if isinstance(args[0], AbstractView):
                request = args[0].request
            else:
                request = args[-1]

            response = web.json_response(context, status=status)
            return response

        return wrapped

    return wrapper


def template_view(tpl_name, **kwargs):
    @template(tpl_name)
    async def view(request):
        return kwargs

    return view


async def setup(app):
    procs = [aiohttp_jinja2.request_processor]
    # setup Jinja2 template renderer
    app_loaders = []
    app_loaders.append(jinja2.FileSystemLoader(os.path.join(settings.BASE_DIR, "app/views/")))
    app_loaders.append(jinja2.PackageLoader("aioweb", "views/"))
    for app_name in settings.APPS:
        try:
            app_loaders.append(jinja2.PackageLoader(app_name, "views"))
        except ImportError as e:
            pass
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.ChoiceLoader(app_loaders),
        context_processors=procs,
        trim_blocks=True,
        lstrip_blocks=True,
        extensions=[DjangoStatic, DjangoLoad,
                    DjangoCsrf, DjangoUrl,
                    DjangoTrans])
