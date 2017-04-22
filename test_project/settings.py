import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

APPS = [
    'aioweb.contrib.admin',
    'aioweb.contrib.auth',
]

MIDDLEWARES = [
    'aioweb.middleware.error_mailer'
]
