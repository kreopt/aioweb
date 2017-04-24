import sys
import os

brief = "rollback all datebase migrations"
aliases = []


def usage(argv0):
    print("Usage: {} db reset".format(argv0))
    sys.exit(1)


def execute(argv, argv0, engine):
    import lib, importlib
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    from aioweb import settings
    sys.path.append(os.getcwd())
    environment = os.getenv("AIOWEB_ENV", "development")

    if '-h' in argv or '--help' in argv:
        usage(argv0)
    oldcwd = os.getcwd()
    os.makedirs(os.path.join(settings.BASE_DIR, 'db'), exist_ok=True)

    os.chdir(os.path.join(settings.BASE_DIR, 'db'))

    print("[ app ]")
    migrations_dir = lib.dirs(settings, format=["migrations"], check=True)
    os.system("orator migrate:reset -c %(base)s/config/database.yml -p %(egg)s -d %(environment)s -n" % {
        'environment': environment,
        'base': settings.BASE_DIR,
        'egg': migrations_dir,
    })
    os.chdir(oldcwd)
