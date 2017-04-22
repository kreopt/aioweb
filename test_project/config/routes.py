import os
from aioweb.conf import settings
from aioweb.util import package_path


def setup(router):
    router.root('test#index')
    router.get('test#test')
    with router.proxy('test#index', is_action=True, name="test") as subroute:
        subroute.get('page1#index')
        subroute.post('/page1/', 'page1#csrf')
        subroute.get('page2#index')

    # with router.constrained(checks=[authenticated]) as auth_router:
    #     auth_router.use('/admin/', 'aioweb.admin')

    router.static('/static/', [
        os.path.join(package_path('aioweb'), 'assets'),
        os.path.join(settings.BASE_DIR, 'app/assets'),
    ])
