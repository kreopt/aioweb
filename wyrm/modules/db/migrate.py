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
    flags = []
    if '--no-input' in argv or '-n' in argv:
        flags.append('-n -f')

    oldcwd = os.getcwd()

    os.makedirs(os.path.join(settings.BASE_DIR, 'db'), exist_ok=True)
    os.chdir(os.path.join(settings.BASE_DIR, 'db'))

    # for app in settings.APPS:
    #    print("[ %s ]" % app)
    #    migrations_dir = lib.dirs(settings, format=["migrations"], app=app)
    #    print("%(migrations_dir)s" % {'migrations_dir': migrations_dir})

    #    os.system("echo y | orator migrate -c %(base)s/config/database.yml -p %(migrations_dir)s -d %(environment)s" % {
    #        'environment': environment,
    #        'base': settings.BASE_DIR,
    #        'migrations_dir': migrations_dir,
    #    })

    migrations_dir = lib.dirs(settings, format=["migrations"])

    os.system("orator migrate -c %(base)s/config/database.yml "
              "--migration-config %(base)s/config/migrations.yml "
              "-p %(migrations_dir)s "
              "-d %(environment)s %(flags)s" % {
                  'environment': environment,
                  'base': settings.BASE_DIR,
                  'migrations_dir': migrations_dir,
                  'flags': ' '.join(flags)
              })

    os.chdir(oldcwd)
