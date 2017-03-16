import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODULES = [
    # 'admin',
    'db',
    # 'session',
    # 'auth',
    'render',
    'email'
]

APPS = [
    'aioweb.admin',
    'aioweb.auth',
]