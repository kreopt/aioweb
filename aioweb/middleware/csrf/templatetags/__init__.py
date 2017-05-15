from jinja2.ext import Extension
from jinja2 import nodes

import aioweb.middleware.csrf


class CsrfTag(Extension):
    """
    Implements django's `{% csrf_token %}` tag.
    """
    tags = set(['csrf_token'])

    def parse(self, parser):
        lineno = parser.stream.expect('name:csrf_token').lineno
        controller = parser.environment.globals.get('controller')
        if controller:
            csrf_token = getattr(controller.request, 'csrf_token', '')
        else:
            csrf_token = ''
        call = self.call_method(
            '_csrf_token',
            [nodes.Const(csrf_token)],  # nodes.Name('csrf_token', 'load', lineno=lineno)
            lineno=lineno
        )
        return nodes.Output([nodes.MarkSafe(call)])

    def _csrf_token(self, csrf_token):
        if not csrf_token or csrf_token == 'NOTPROVIDED':
            return ''
        else:
            return '<input type="hidden" name="{}" value="{}" />'.format(aioweb.middleware.csrf.CSRF_FIELD_NAME,
                                                                         csrf_token)
