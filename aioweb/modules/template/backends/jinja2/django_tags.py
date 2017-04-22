from urllib.parse import urljoin

from jinja2 import lexer, nodes
from jinja2.ext import Extension

from aioweb.conf import settings

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
