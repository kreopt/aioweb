import traceback
import warnings
from datetime import datetime
from urllib.parse import urljoin

from jinja2 import lexer, nodes
from jinja2.ext import Extension

from aioweb.conf import settings


# see jinja2-django-tags

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
        app = self.environment.globals['app']
        tail = ''
        # if app['env'] == 'development':
        #     tail = '?%s' % random.randint(0, 999999)
        return "%s%s" % (urljoin(settings.STATIC_URL, path), tail)

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


class DjangoNow(Extension):
    """
    Implements django's `{% now %}` tag.
    """
    tags = set(['now'])

    def _now(self, format_string):
        tzinfo = None  # get_current_timezone() if settings.USE_TZ else None
        cur_datetime = datetime.now(tz=tzinfo)
        return cur_datetime.strftime(format_string)

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        token = parser.stream.expect(lexer.TOKEN_STRING)
        format_string = nodes.Const(token.value)
        call = self.call_method('_now', [format_string], lineno=lineno)

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

    def _url_reverse(self, controller, name, *args, **kwargs):
        if 'query_' in kwargs:
            query = kwargs.pop('query_')
        else:
            query = None

        try:
            backend_name = controller.router.backendName
        except:
            backend_name = ''
        router = self.environment.globals['app'].router
        try:
            url = router.get(f'{backend_name}:{name}', router.get(name)).url_for(**kwargs)
        except Exception as e:
            warnings.warn(f'Failed to reverse url {name} with {len(args)} args and {len(kwargs)} kwargs')
            traceback.print_exc()
            return '#'

        if query:
            url = url.with_query(query)

        return url

        # if len(kwargs):
        #     return self.environment.globals['url'](name, parts=kwargs)
        # else:
        #     return self.environment.globals['url'](name)

    @staticmethod
    def parse_expression(parser):
        # Due to how the jinja2 parser works, it treats "foo" "bar" as a single
        # string literal as it is the case in python.
        # But the url tag in django supports multiple string arguments, e.g.
        # "{% url 'my_view' 'arg1' 'arg2' %}".
        # That's why we have to check if it's a string literal first.
        token = parser.stream.current
        if token.test(lexer.TOKEN_STRING):
            expr = nodes.Const(token.value, lineno=token.lineno)
            next(parser.stream)
        else:
            expr = parser.parse_expression(False)

        return expr

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        view_name = parser.stream.expect(lexer.TOKEN_STRING)
        view_name = nodes.Const(view_name.value, lineno=view_name.lineno)

        args = None
        kwargs = None
        as_var = None

        while parser.stream.current.type != lexer.TOKEN_BLOCK_END:
            token = parser.stream.current
            if token.test('name:as'):
                next(parser.stream)
                token = parser.stream.expect(lexer.TOKEN_NAME)
                as_var = nodes.Name(token.value, 'store', lineno=token.lineno)
                break
            if args is not None:
                args.append(self.parse_expression(parser))
            elif kwargs is not None:
                if token.type != lexer.TOKEN_NAME:
                    parser.fail(
                        "got '{}', expected name for keyword argument"
                        "".format(lexer.describe_token(token)),
                        lineno=token.lineno
                    )
                arg = token.value
                next(parser.stream)
                parser.stream.expect(lexer.TOKEN_ASSIGN)
                token = parser.stream.current
                kwargs[arg] = self.parse_expression(parser)
            else:
                if parser.stream.look().type == lexer.TOKEN_ASSIGN:
                    kwargs = {}
                else:
                    args = []
                continue

        if args is None:
            args = []
        args.insert(0, view_name)
        args.insert(0, nodes.Name('controller', 'load', lineno=lineno))

        if kwargs is not None:
            kwargs = [nodes.Keyword(key, val) for key, val in kwargs.items()]

        call = self.call_method('_url_reverse', args, kwargs, lineno=lineno)
        if as_var is None:
            return nodes.Output([call], lineno=lineno)
        else:
            return nodes.Assign(as_var, call, lineno=lineno)
