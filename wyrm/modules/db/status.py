import sys
import os

brief="show the status of migrations"
aliases=[]
def usage(argv0):
    print("Usage: {} db status".format(argv0))
    sys.exit(1)

def execute(argv, argv0, engine):
    import lib, importlib
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    from aioweb import settings
    sys.path.append( os.getcwd() )
    environment = os.getenv("AIOWEB_ENV", "development")

    if '-h' in argv or '--help' in argv:
        usage(argv0)
    oldcwd = os.getcwd()
    try:
        os.mkdir(os.path.join(settings.BASE_DIR, 'db'))
    except: pass

    os.chdir(os.path.join(settings.BASE_DIR, 'db'))

    for app in settings.APPS:
        migrations_dir=lib.dirs(settings, app=app, format=["migrations"], check=True)
        if migrations_dir:
            print("[ %s ]" % app)
            os.system("orator migrate:status -c %(base)s/config/database.yml -p %(egg)s -d %(environment)s" % {
                'environment': environment,
                'base': settings.BASE_DIR,
                'egg': migrations_dir,
            })
    print("[ app ]")
    migrations_dir=lib.dirs(settings, format=["migrations"], check=True)
    os.system("orator migrate:status -c %(base)s/config/database.yml -p %(egg)s -d %(environment)s" % {
        'environment': environment,
        'base': settings.BASE_DIR,
        'egg': migrations_dir,
    })
    os.chdir(oldcwd)


