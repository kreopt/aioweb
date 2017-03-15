import os
from aioweb.conf import settings


def setup(router):
    router.root('test#index')
    router.get('test#test')
