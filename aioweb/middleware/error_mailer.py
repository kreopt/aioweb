import traceback

import aiosmtplib
from aiohttp import web
from aiohttp.log import web_logger

from aioweb.conf import settings
from aioweb.util import awaitable
from aioweb.modules.email import send_mail


async def mail_traceback(request):
    if request.app.get('env', 'development') == 'development':
        traceback.print_exc()
    else:
        trace = traceback.format_exc()
        try:
            # Create a text/plain message
            if request.content_type == 'multipart/form-data':
                post = '<multipart>'
            else:
                post = await request.post()

            await send_mail(request.app,
                            sender='%s service <noreply@%s>' % (settings.BRAND, request.url.host),
                            recipients=tuple(e for e in getattr(settings, 'ADMINS', [])),
                            subject='%s error report at %s -> %s' % (settings.BRAND, request.method, request.url),
                            body="%s\n\nmatch:\n%s\n\nPOST:\n%s\n\nGET:\n%s\n\nHEADERS:\n%s" % (
                                trace,
                                request.match_info,
                                post,
                                request.query,
                                request.headers
                            ))

        except aiosmtplib.errors.SMTPConnectError as e:
            web_logger.warn("Failed to connect to SMTP server\n%s" % e.message)
            print(trace)
        except Exception as e:
            traceback.print_exc()
            print(trace)


async def middleware(app, handler):
    async def middleware_handler(request):
        try:
            return await awaitable(handler(request))
        except (web.HTTPClientError, web.HTTPRedirection) as e:
            raise e
        except web.HTTPServerError as e:
            await mail_traceback(request)
            raise e
        except Exception as e:
            await mail_traceback(request)
            raise e

    return middleware_handler
