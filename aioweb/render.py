import functools
import os
from urllib.parse import urljoin

import aiohttp_jinja2
import asyncio
import jinja2
from aiohttp import web
from aiohttp.abc import AbstractView
from aiohttp_jinja2 import template as template, render_string, render_template
from jinja2.ext import Extension
from jinja2 import lexer, nodes
from aioweb.conf import settings


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

class DjangoLoad(Extension):
    """
    Implements django's `{% load %}` tag.
    """
    tags = set(['load'])

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        token = parser.stream.expect(lexer.TOKEN_NAME)
        path = nodes.Const(token.value)
        call = self.call_method(
            '_load',
            [],
            lineno=lineno
        )
        return nodes.Output([call])

    def _load(self):
        return ''

class DjangoTrans(Extension):
    """
    Implements django's `{% trans %}` tag.
    """
    tags = set(['trans'])

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        token = parser.stream.expect(lexer.TOKEN_STRING)
        path = nodes.Const(token.value)
        call = self.call_method(
            '_trans',
            [path],
            lineno=lineno
        )
        return nodes.Output([call])

    def _trans(self, str):
        return str

class DjangoCsrf(Extension):
    """
    Implements django's `{% csrf_token %}` tag.
    """
    tags = set(['csrf_token'])

    def parse(self, parser):
        lineno = parser.stream.expect('name:csrf_token').lineno
        call = self.call_method(
            '_csrf_token',
            [nodes.Name('csrf_token', 'load', lineno=lineno)],
            lineno=lineno
        )
        return nodes.Output([nodes.MarkSafe(call)])

    def _csrf_token(self, csrf_token):
        if not csrf_token or csrf_token == 'NOTPROVIDED':
            return ''
        else:
            return '<input type="hidden" name="csrfmiddlewaretoken" value="{}" />'.format(csrf_token)


class DjangoStatic(Extension):
    """
    Implements django's `{% static %}` tag::
        My static file: {% static 'my/static.file' %}
        {% static 'my/static.file' as my_file %}
        My static file in a var: {{ my_file }}
    """
    tags = set(['static'])

    def _static(self, path):
        return urljoin(settings.STATIC_URL, path)

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        token = parser.stream.expect(lexer.TOKEN_STRING)
        path = nodes.Const(token.value)
        call = self.call_method('_static', [path], lineno=lineno)

        token = parser.stream.current
        if token.test('name:as'):
            next(parser.stream)
            as_var = parser.stream.expect(lexer.TOKEN_NAME)
            as_var = nodes.Name(as_var.value, 'store', lineno=as_var.lineno)
            return nodes.Assign(as_var, call, lineno=lineno)
        else:
            return nodes.Output([call], lineno=lineno)

class DjangoUrl(Extension):
    """
    Implements django's `{% ulr %}` tag::
        My url: {% url 'url' %}
        {% static 'url' as my_url %}
        My url in a var: {{ my_ulr }}
    """
    tags = set(['url'])

    def _url(self, path):
        return self.environment.globals['url'](path)

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        token = parser.stream.expect(lexer.TOKEN_STRING)
        path = nodes.Const(token.value)


        call = self.call_method('_url', [path], lineno=lineno)

        token = parser.stream.current
        if token.test('name:as'):
            next(parser.stream)
            as_var = parser.stream.expect(lexer.TOKEN_NAME)
            as_var = nodes.Name(as_var.value, 'store', lineno=as_var.lineno)
            return nodes.Assign(as_var, call, lineno=lineno)
        else:
            return nodes.Output([call], lineno=lineno)


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
    app_loaders.append(jinja2.PackageLoader("aioweb",  "views/"))
    for app_name in settings.APPS:
        try:
            app_loaders.append(jinja2.PackageLoader(app_name, "views"))
        except ImportError as e:
            pass
    aiohttp_jinja2.setup(
        app, loader=jinja2.ChoiceLoader(app_loaders), context_processors=procs, extensions=[DjangoStatic, DjangoLoad,
                                                                                            DjangoCsrf, DjangoUrl, DjangoTrans])
