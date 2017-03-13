import os

from aioweb.conf import settings

def setup(router):
    router.use('landing')
    router.use('cabinet', prefix='/cabinet/', name='cabinet')
    router.use('aioweb.admin', prefix='/admin/', name='admin')
    router.app.router.add_static("%sadmin/" % settings.STATIC_URL, path=os.path.join(settings.BASE_DIR, 'aioweb/admin/static/admin/'), name='admin_static')
    router.app.router.add_static(settings.STATIC_URL, path=os.path.join(settings.BASE_DIR, 'app/core/static'), name='static')
