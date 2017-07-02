from aiohttp import web
from aiohttp_session import get_session, SESSION_KEY as SESSION_COOKIE_NAME

from aioweb.middleware.csrf.templatetags import CsrfTag, CsrfRawTag
from aioweb.util import awaitable
from aioweb.modules.template.backends.jinja2 import APP_KEY as JINJA_APP_KEY
import random, string
from aiohttp_session import get_session


CSRF_FIELD_NAME = 'csrftoken'
CSRF_SESSION_NAME = 'csrf_token'
CSRF_HEADER_NAME = 'X-Csrf-Token'
CSRF_COOKIE_NAME = 'Csrf-Token'

REASON_NO_CSRF_COOKIE = "CSRF cookie not set."
REASON_BAD_TOKEN = "CSRF token missing or incorrect."

CSRF_LENGTH = 128
CSRF_ALLOWED_CHARS = string.ascii_letters + string.digits

def generate_csrf_token():
    return ''.join([random.choice(CSRF_ALLOWED_CHARS) for c in range(CSRF_LENGTH)])

async def get_token(request):
    """
    Returns the CSRF token required for a POST form. The token is an
    alphanumeric value. A new token is created if one is not already set.
    """
    session = await get_session(request)
    if CSRF_SESSION_NAME in session and session[CSRF_SESSION_NAME]:
        return session[CSRF_SESSION_NAME]
    return await set_token(request)

async def set_token(request):
    session = await get_session(request)
    session[CSRF_SESSION_NAME] = generate_csrf_token()
    return session[CSRF_SESSION_NAME]


async def middleware(app, handler):
    async def middleware_handler(request):

        setattr(request, 'csrf_token', await get_token(request))

        try:
            response = await awaitable(handler(request))
        except web.HTTPException as e:
            raise e

        return response

    return middleware_handler


def setup(app):
    app[JINJA_APP_KEY].add_extension(CsrfTag)
    app[JINJA_APP_KEY].add_extension(CsrfRawTag)


async def pre_dispatch(request, controller, actionName):
    reason = None

    check_ok = True
    if request.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):

        action = getattr(controller, actionName)

        if not getattr(action, 'csrf_disabled', False):
            check_ok = False
            token = await get_token(request)
            if token:
                # TODO: check referer

                data = await request.post()
                requesttoken = data.get(CSRF_FIELD_NAME, request.headers.get(CSRF_HEADER_NAME, ''))
                if requesttoken == token:
                    check_ok = True
                else:
                    reason = REASON_BAD_TOKEN
            else:
                reason = REASON_NO_CSRF_COOKIE

    if not check_ok:
        raise web.HTTPForbidden(reason=reason)
