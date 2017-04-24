import sys
import os

brief = "migrate the database"


def usage(argv0):
    print("Usage: {} db migrate".format(argv0))
    sys.exit(1)


aliases = ['m']


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
    migrations_dir = lib.dirs(settings, format=["migrations"])

    os.system("echo y | orator migrate -c %(base)s/config/database.yml -p %(migrations_dir)s -d %(environment)s" % {
        'environment': environment,
        'base': settings.BASE_DIR,
        'migrations_dir': migrations_dir,
    })
    os.chdir(oldcwd)
