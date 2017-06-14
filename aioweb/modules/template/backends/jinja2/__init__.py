import importlib
import os
import traceback

import aiohttp_jinja2
import jinja2
from aioweb.util import awaitable

from aioweb.conf import settings

from .django_tags import DjangoStatic, DjangoLoad, DjangoUrl, DjangoTrans, DjangoNow

from aiohttp_jinja2 import render_string, render_template as render, APP_KEY


async def setup(app):
    procs = [aiohttp_jinja2.request_processor]
    # setup Jinja2 template renderer
    app_loaders = [
        jinja2.FileSystemLoader(os.path.join(settings.BASE_DIR, "app/views/")),
        jinja2.PackageLoader("aioweb", "views/")
    ]
    for app_name in settings.APPS:
        try:
            app_loaders.append(jinja2.PackageLoader(app_name, "app/views"))
        except ImportError as e:
            pass
    env = aiohttp_jinja2.setup(
        app,
        loader=jinja2.ChoiceLoader(app_loaders),
        context_processors=procs,
        trim_blocks=True,
        lstrip_blocks=True,
        extensions=[
            DjangoStatic,
            DjangoUrl,
            DjangoNow,
            DjangoTrans
        ])

    env.globals['settings'] = settings

    try:
        mod = importlib.import_module("app")
        setup = getattr(mod, 'setup_template')
        await awaitable(setup(env))
    except (ImportError, AttributeError) as e:
        pass
