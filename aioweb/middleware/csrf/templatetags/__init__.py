from jinja2.ext import Extension
from jinja2 import nodes

import aioweb.middleware.csrf


class CsrfTag(Extension):
    """
    Implements `{% csrf_token %}` tag.
    """
    tags = set(['csrf_token'])


    def parse(self, parser):
        self.parser = parser
        lineno = parser.stream.expect('name:csrf_token').lineno
        call = self.call_method(
            '_csrf_token',
            [
                nodes.Getattr(nodes.Name('request', 'load'), 'csrf_token', 'load')
            ],
            lineno=lineno
        )
        return nodes.Output([nodes.MarkSafe(call)])

    def _csrf_token(self, csrf_token):
        # request = self.parser.environment.globals.get('request')
        # csrf_token = getattr(request, 'csrf_token', '')
        if not csrf_token or csrf_token == 'NOTPROVIDED':
            return ''
        else:
            return '<input type="hidden" name="{}" value="{}" />'.format(aioweb.middleware.csrf.CSRF_FIELD_NAME,
                                                                         csrf_token)
class CsrfRawTag(Extension):
    """
    Implements `{% csrf_token_value %}` tag.
    """
    tags = set(['csrf_token_raw'])


    def parse(self, parser):
        self.parser = parser
        lineno = parser.stream.expect('name:csrf_token_raw').lineno
        call = self.call_method(
            '_csrf_token',
            [nodes.Getattr(nodes.Name('request', 'load'), 'csrf_token', 'load')],
            lineno=lineno
        )
        return nodes.Output([nodes.MarkSafe(call)])

    def _csrf_token(self, csrf_token):
        if not csrf_token or csrf_token == 'NOTPROVIDED':
            return ''
        else:
            return csrf_token
