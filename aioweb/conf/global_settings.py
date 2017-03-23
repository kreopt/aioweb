BRAND = 'Aioweb'
ADMINS = []
MODULES = [
    'db',
    'session',
    'auth',
    'render',
    'email'
]
APPS = []
MIDDLEWARES = [
    'aioweb.middleware.error_mailer'
]

STATIC_URL = '/static/'

CONFIG = {
}
