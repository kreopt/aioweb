from aioweb.util import handler_as_coroutine
from aioweb.util.csrf import get_token

async def middleware(app, handler):
    async def middleware_handler(request):
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            # TODO: check csrf
            if hasattr(request, 'is_ajax') and request.is_ajax():
                token = request.headers.get('X-Csrf-Token')
            else:
                pass
        setattr(request, 'csrf_token', get_token(request))
        return await handler_as_coroutine(handler)(request)
    return middleware_handler
