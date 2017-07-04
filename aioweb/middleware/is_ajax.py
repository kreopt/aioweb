from aioweb.util import awaitable


async def middleware(app, handler):
    async def middleware_handler(request):
        setattr(request, 'is_ajax', lambda: request.headers.get('X-Requested-With', '').lower() == 'xmlhttprequest')
        return await awaitable(handler(request))

    return middleware_handler
