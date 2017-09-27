import email
from email.message import EmailMessage

import aiosmtplib
from aioweb.conf import settings


async def send_mail(app,
                    sender='%s service <%s>' % (settings.BRAND, settings.SERVER_EMAIL),
                    recipients=tuple(),
                    subject='',
                    body=''):
    if not len(recipients):
        return
    async with app.smtp as conn:

        msg = EmailMessage()

        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = ', '.join(recipients)

        msg.set_content(body)

        return await conn.send_message(msg, sender, recipients, timeout=5)


async def setup(app):
    setattr(app, 'smtp', aiosmtplib.SMTP(hostname=app.conf.get('email.host', 'localhost'),
                                         port=app.conf.get('email.port', 25),
                                         timeout=app.conf.get('email.timeout', 5),
                                         loop=app.loop))
