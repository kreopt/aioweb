import os
from aioweb.conf import settings
from aioweb.util import package_path


def setup(router):
    router.set_view_prefix('aioweb_admin') # TODO: move to config

    router.root('admin#index', name='index')
    router.resource('{model:[a-z0-9_]+}', 'modeladmin')
