import email
import aiosmtplib

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
