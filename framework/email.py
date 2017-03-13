import email
import traceback

import aiosmtplib
from aiohttp import web
from aiohttp.log import web_logger

from framework import settings

async def mail_traceback(request):
    trace = traceback.format_exc()
    try:
        await request.app.smtp.connect()
        # Create a text/plain message
        await request.post()
        msg = email.message_from_string("%s\n\nmatch:\n%s\n\nPOST:\n%s\n\nGET:\n%s" % (
            trace,
            request.match_info,
            request.POST,
            request.GET
        ))

        msg['Subject'] = 'Streamedian.com error report at %s:%s' % (request.method, request.url)
        msg['From'] = 'Streamedian service <noreply@streamedian.com>'
        msg['To'] = 'kreopt@specforge.com'

        await request.app.smtp.send_message(msg, 'noreply@streamedian.com', getattr(settings, 'ADMINS', []))
    except aiosmtplib.errors.SMTPConnectError as e:
        web_logger.warn("Failed to connect to SMTP server\n%s" % e.message)
        print(trace)

async def error_mailer(app, handler):
    async def middleware_handler(request):
        try:
            return await handler(request)
        except (web.HTTPClientError, web.HTTPRedirection) as e:
            raise e
        except web.HTTPServerError as e:
            await mail_traceback(request)
            raise e
        except Exception as e:
            await mail_traceback(request)
            raise e
    return middleware_handler

async def send_mail(app,
                    sender='Streamedian service <noreply@streamedian.com>',
                    recipients=tuple(),
                    subject='',
                    body=''):
    if not len(recipients): return
    await app.smtp.connect()

    msg = email.message_from_string(body)

    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)

    return await app.smtp.send_message(msg, sender, recipients)

async def setup(app):
    setattr(app, 'smtp', aiosmtplib.SMTP(hostname='localhost', port=25, loop=app.loop))
