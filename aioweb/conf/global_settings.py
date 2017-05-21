import os
import platform

BRAND = 'Aioweb'
SERVER_EMAIL = 'aioweb@%s' % platform.node()
TEMPLATE_BACKEND = 'jinja2'

ADMINS = []
MODULES = [
    'db',
    'session',
    'template',
    'email'
]
APPS = []
MIDDLEWARES = [
    'aioweb.middleware.error_mailer'
]

STATIC_URL = '/static/'

BASE_DIR = os.getcwd()

CONFIG = {
}
