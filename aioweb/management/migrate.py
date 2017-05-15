import importlib.util
import os

from aioweb import settings


def run(*args, **kwargs):
    oldcwd = os.getcwd()
    try:
        os.mkdir(os.path.join(settings.BASE_DIR, 'db'))
    except:
        pass

    os.chdir(os.path.join(settings.BASE_DIR, 'db'))
    print("[ app ]")

    os.system("orator migrate -c %(base)s/config/database.yml -p %(base)s/db/migrations/" % {
        'base': settings.BASE_DIR
    })

    for app in settings.APPS:
        print("[ %s ]" % app)
        print("%(egg)s/migrations/" % {'egg': os.path.dirname(importlib.util.find_spec(app).origin)})
        os.system("orator migrate -c %(base)s/config/database.yml -p %(egg)s/migrations/" % {
            'base': settings.BASE_DIR,
            'egg': os.path.dirname(importlib.util.find_spec(app).origin)
        })
    os.chdir(oldcwd)
