from aioweb.util import handler_as_coroutine


async def method_override(app, handler):
    async def middleware_handler(request):
        http_method = request.headers.get('X-Http-Method-Override').upper()
        overriden = request.clone(method=http_method) if http_method else request
        return await handler_as_coroutine(handler)(overriden)

    return middleware_handler
