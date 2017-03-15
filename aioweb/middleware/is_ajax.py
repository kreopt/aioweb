from aioweb.util import handler_as_coroutine


async def is_ajax_middleware(app, handler):
    async def middleware_handler(request):
        setattr(request, 'is_ajax', lambda: request.headers.get('X-Requested-With') == 'XMLHttpRequest')
        return await handler_as_coroutine(handler)(request)
    return middleware_handler