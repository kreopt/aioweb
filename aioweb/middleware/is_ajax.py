from aiohttp import web

from aioweb.util import awaitable


@web.middleware
def is_ajax_middleware(request, handler):
    setattr(request, 'is_ajax', lambda: request.headers.get('X-Requested-With', '').lower() == 'xmlhttprequest')
    return awaitable(handler(request))

