import traceback

import aiosmtplib
from aiohttp import web
from aiohttp.log import web_logger

from aioweb.conf import settings
from aioweb.util import handler_as_coroutine
from aioweb.email import send_mail


async def mail_traceback(request):
    trace = traceback.format_exc()
    try:
        # Create a text/plain message
        await request.post()

        await send_mail(request.app,
                  sender='%s service <noreply@%s>' % (settings.BRAND, request.url.host),
                  recipients=tuple(e for e in getattr(settings, 'ADMINS', [])),
                  subject='%s error report at %s -> %s' % (settings.BRAND, request.method, request.url),
                  body="%s\n\nmatch:\n%s\n\nPOST:\n%s\n\nGET:\n%s\n\nHEADERS:\n%s" % (
                        trace,
                        request.match_info,
                        request.POST,
                        request.GET,
                        request.headers
                    ))

    except aiosmtplib.errors.SMTPConnectError as e:
        web_logger.warn("Failed to connect to SMTP server\n%s" % e.message)
        print(trace)


async def error_mailer(app, handler):
    async def middleware_handler(request):
        try:
            return await handler_as_coroutine(handler)(request)
        except (web.HTTPClientError, web.HTTPRedirection) as e:
            raise e
        except web.HTTPServerError as e:
            await mail_traceback(request)
            raise e
        except Exception as e:
            await mail_traceback(request)
            raise e
    return middleware_handler