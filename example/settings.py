import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASES = {
    'default': {
        'driver': 'sqlite',
        'database': os.path.join(BASE_DIR,'db.sqlite3')
    }
}
MODULES = [
    # 'admin',
    # 'db',
    # 'session',
    # 'auth',
    'render',
    'email'
]
