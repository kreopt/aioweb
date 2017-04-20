from aiohttp import web

from aioweb.util import awaitable
from aioweb.util.csrf import make_csrf_token, unsalt_cipher_token, sanitize_token, compare_salted_tokens

CSRF_FIELD_NAME = 'csrftoken'
CSRF_HEADER_NAME = 'X-Csrf-Token'
CSRF_COOKIE_NAME = 'Csrf-Token'

REASON_NO_REFERER = "Referer checking failed - no Referer."
REASON_BAD_REFERER = "Referer checking failed - %s does not match any trusted origins."
REASON_NO_CSRF_COOKIE = "CSRF cookie not set."
REASON_BAD_TOKEN = "CSRF token missing or incorrect."
REASON_MALFORMED_REFERER = "Referer checking failed - Referer is malformed."
REASON_INSECURE_REFERER = "Referer checking failed - Referer is insecure while host is secure."


def get_token(request):
    """
    Returns the CSRF token required for a POST form. The token is an
    alphanumeric value. A new token is created if one is not already set.

    A side effect of calling this function is to make the csrf_protect
    decorator and the CsrfViewMiddleware add a CSRF cookie and a 'Vary: Cookie'
    header to the outgoing response.  For this reason, you may need to use this
    function lazily, as is done by the csrf context processor.
    """
    cookietoken = sanitize_token(request.cookies.get(CSRF_COOKIE_NAME, request.headers.get(CSRF_HEADER_NAME, '')))
    return make_csrf_token(unsalt_cipher_token(cookietoken) if cookietoken else None)


async def middleware(app, handler):
    async def middleware_handler(request):
        reason = None
        need_refresh = False
        if request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            check_ok = True
        else:
            check_ok = False
            cookietoken = sanitize_token(request.cookies.get(CSRF_COOKIE_NAME, request.headers.get(CSRF_HEADER_NAME, '')))

            if cookietoken:
                # TODO: check referer

                data = await request.post()
                requesttoken = sanitize_token(data.get(CSRF_FIELD_NAME, ''))
                if compare_salted_tokens(requesttoken, cookietoken):
                    check_ok = True
                else:
                    reason = REASON_BAD_TOKEN
            else:
                need_refresh = True
                reason = REASON_NO_CSRF_COOKIE

        setattr(request, 'csrf_token', get_token(request))

        if check_ok:
            response = await awaitable(handler(request))
            if not request.cookies.get(CSRF_COOKIE_NAME) or need_refresh:
                response.set_cookie(CSRF_COOKIE_NAME, request.csrf_token)
                response.headers[CSRF_HEADER_NAME] = request.csrf_token
            return response
        else:
            response = web.HTTPForbidden(reason=reason)
            response.set_cookie(CSRF_COOKIE_NAME, request.csrf_token)
            response.headers[CSRF_HEADER_NAME] = request.csrf_token
            raise response
    return middleware_handler
