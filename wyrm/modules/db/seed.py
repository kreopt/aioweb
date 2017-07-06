import sys
import os

brief = "seed the database"


def usage(argv0):
    print("Usage: {} db seed".format(argv0))
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

    for app in settings.APPS:
        print("[ %s ]" % app)
        seeds_dir = lib.dirs(settings, format=["seeds"], app=app)
        print("%(seeds_dir)s" % {'seeds_dir': seeds_dir})

        os.system("orator db:seed -c %(base)s/config/database.yml -p %(seeds_dir)s -d %(environment)s -f" % {
            'environment': environment,
            'base': settings.BASE_DIR,
            'seeds_dir': seeds_dir,
        })

    print("[ app ]")
    seeds_dir = lib.dirs(settings, format=["seeds"])
    print("%(seeds_dir)s" % {'seeds_dir': seeds_dir})

    os.system("orator db:seed -c %(base)s/config/database.yml -p %(seeds_dir)s -d %(environment)s -f" % {
        'environment': environment,
        'base': settings.BASE_DIR,
        'seeds_dir': seeds_dir,
    })

    os.chdir(oldcwd)

