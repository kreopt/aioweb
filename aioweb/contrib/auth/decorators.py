from aiohttp import web

from aioweb.core.controller.decorators import before_action


def auth_or_403(redirect_to):
    def decorated(self):
        if not self.request.user.is_authenticated():
            if redirect_to:
                raise web.HTTPFound(redirect_to)
            else:
                raise web.HTTPForbidden(reason='Unauthorized')

    return decorated


def authenticated(redirect_to=None, only=tuple(), exclude=()):
    return before_action(auth_or_403(redirect_to), only, exclude)


def check_logged(redirect_to=None):
    async def fn(request, controller, actionName):
        if not request.user.is_authenticated():
            if redirect_to:
                raise web.HTTPFound(redirect_to)
            else:
                raise web.HTTPForbidden(reason='Unauthorized')

    return fn
