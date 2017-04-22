import email
import aiosmtplib
from aioweb.conf import settings


async def send_mail(app,
                    sender='%s service <%s>' % (settings.BRAND, settings.SERVER_EMAIL),
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
    setattr(app, 'smtp', aiosmtplib.SMTP(hostname = app.conf.get('email.host', 'localhost'),
                                         port     = app.conf.get('email.port', 25),
                                         loop     = app.loop))
