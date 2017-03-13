import os

from framework import settings


def run(app_name, migration_name, *args, **kwargs):
    os.system("orator make:migration %s -p %s/migrations/ %s" % (migration_name,
                                                         os.path.join(settings.BASE_DIR, 'app', app_name.replace('.', '/')),
                                                         ''.join(args))
              )
