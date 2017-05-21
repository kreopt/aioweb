import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

APPS = [
    'aioweb_admin',
    'aioweb_auth',
]

MIDDLEWARES = [
    'aioweb.middleware.error_mailer'
]
