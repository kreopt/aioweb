import os
from aioweb.conf import settings
from aioweb.router import AuthenticatedContext
from aioweb.util import package_path


def setup(router):
    router.root('site#index')
    router.get('site#test')

    router.static('/static/', [
        os.path.join(package_path('aioweb'), 'assets'),
        os.path.join(settings.BASE_DIR, 'app/assets'),
    ])
