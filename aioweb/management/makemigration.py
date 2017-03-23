import os

from aioweb import settings


def run(app, migration_name, *args, **kwargs):
    os.mkdir(os.path.join(settings.BASE_DIR, 'db/migrations/'))
    os.system("orator make:migration %(name)s -p %(base)s/db/migrations/ %(args)s" % {
        'name': migration_name,
        'base': settings.BASE_DIR,
        'args': ''.join(args)
    })
