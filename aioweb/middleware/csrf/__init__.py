from aiohttp import web
from aiohttp_session import get_session, SESSION_KEY as SESSION_COOKIE_NAME

from aioweb.middleware.csrf.templatetags import CsrfTag
from aioweb.util import awaitable
from .csrf import make_csrf_token, unsalt_cipher_token, sanitize_token, compare_salted_tokens
from aioweb.modules.template.backends.jinja2 import APP_KEY as JINJA_APP_KEY

CSRF_FIELD_NAME = 'csrftoken'
CSRF_HEADER_NAME = 'X-Csrf-Token'
CSRF_COOKIE_NAME = 'Csrf-Token'

REASON_NO_REFERER = "Referer checking failed - no Referer."
REASON_BAD_REFERER = "Referer checking failed - %s does not match any trusted origins."
REASON_NO_CSRF_COOKIE = "CSRF cookie not set."
REASON_BAD_TOKEN = "CSRF token missing or incorrect."
REASON_MALFORMED_REFERER = "Referer checking failed - Referer is malformed."
REASON_INSECURE_REFERER = "Referer checking failed - Referer is insecure while host is secure."

async def get_token(request):
    """
    Returns the CSRF token required for a POST form. The token is an
    alphanumeric value. A new token is created if one is not already set.

    A side effect of calling this function is to make the csrf_protect
    decorator and the CsrfViewMiddleware add a CSRF cookie and a 'Vary: Cookie'
    header to the outgoing response.  For this reason, you may need to use this
    function lazily, as is done by the csrf context processor.
    """
    cookietoken = sanitize_token(request.cookies.get(CSRF_COOKIE_NAME, request.headers.get(CSRF_HEADER_NAME, '')))
    session = await get_session(request)
    return make_csrf_token(unsalt_cipher_token(cookietoken) if cookietoken else session.identity)


def set_token(response, token):
    response.set_cookie(CSRF_COOKIE_NAME, token)
    response.headers[CSRF_HEADER_NAME] = token


def sanitize_request_token(request):
    return sanitize_token(request.cookies.get(CSRF_COOKIE_NAME, request.headers.get(CSRF_HEADER_NAME, '')))


async def middleware(app, handler):
    async def middleware_handler(request):

        session = await get_session(request)
        if session.identity:
            setattr(request, 'csrf_token', await get_token(request))
            cookie_token = sanitize_request_token(request)
        else:
            setattr(request, 'csrf_token', None)
            cookie_token = None

        try:
            response = await awaitable(handler(request))
        except web.HTTPException as e:
            if request.get('just_logged_out'):
                e.del_cookie(CSRF_COOKIE_NAME)
                e.del_cookie(SESSION_COOKIE_NAME)
            elif session.identity and not cookie_token:
                set_token(e, request.csrf_token)
            raise e

        if request.get('just_logged_out'):
            response.del_cookie(CSRF_COOKIE_NAME)
            response.del_cookie(SESSION_COOKIE_NAME)
        elif session.identity and (not cookie_token or request.get('just_authenticated')):
            set_token(response, request.csrf_token)

        return response

    return middleware_handler


def setup(app):
    app[JINJA_APP_KEY].add_extension(CsrfTag)


async def pre_dispatch(request, controller, actionName):
    reason = None

    check_ok = True
    if request.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):

        action = getattr(controller, actionName)

        if not getattr(action, 'csrf_disabled', False):
            check_ok = False
            cookietoken = sanitize_request_token(request)

            check_ok = True
            # if cookietoken:
            #     # TODO: check referer
            #
            #     data = await request.post()
            #     requesttoken = sanitize_token(data.get(CSRF_FIELD_NAME, ''))
            #     if requesttoken and compare_salted_tokens(requesttoken, cookietoken):
            #         check_ok = True
            #     else:
            #         reason = REASON_BAD_TOKEN
            # else:
            #     reason = REASON_NO_CSRF_COOKIE
    if not check_ok:
        raise web.HTTPForbidden(reason=reason)
