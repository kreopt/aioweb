import os

from aioweb import settings


def run(app_name, *args, **kwargs):
    if app_name:
        apps = [app_name]
    else:
        apps = settings.APPS

    for app in apps:
        os.system("orator migrate:rollback -c %s/settings.py -p %s/migrations/" % (
            settings.BASE_DIR,
            os.path.join(settings.BASE_DIR, 'app', app.replace('.', '/'))))
