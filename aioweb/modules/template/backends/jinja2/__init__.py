import os

import aiohttp_jinja2
import jinja2
from aioweb.conf import settings

from .django_tags import DjangoStatic, DjangoLoad, DjangoUrl, DjangoTrans

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
            app_loaders.append(jinja2.PackageLoader(app_name, "views"))
        except ImportError as e:
            pass
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.ChoiceLoader(app_loaders),
        context_processors=procs,
        trim_blocks=True,
        lstrip_blocks=True,
        extensions=[
            DjangoStatic,
            DjangoUrl,
            DjangoTrans
        ])