import sys
import os

brief="migrate the database"
def usage(argv0):
    print("Usage: {} db migrate [app_name|all]".format(argv0))
    sys.exit(1)

aliases=['m']
def execute(argv, argv0, engine):
    import lib, importlib
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    from aioweb import settings
    sys.path.append( os.getcwd() )
    environment = os.getenv("AIOWEB_ENV", "development")

    if '-h' in argv or '--help' in argv:
        usage(argv0)

    oldcwd = os.getcwd()

    if len(argv) != 0 and argv[0] not in settings.APPS+["all"]:
        print("ERROR: can't locate the {} app".format(argv[0]))
        print("available apps: {}".format(", ".join(settings.APPS)))
        usage(argv0)


    os.makedirs(os.path.join(settings.BASE_DIR, 'db'), exist_ok=True)

    def migrate(app):
        migrations_dir=lib.dirs(settings, app=app, format=["migrations"], check=True)
        if not migrations_dir:
            print("No migrations found")
            return
        print("[ %s ]" % app)
        print(migrations_dir)
        os.system("echo y | orator migrate -c %(base)s/config/database.yml -p %(egg)s -d %(environment)s" % {
            'environment': environment,
            'base': settings.BASE_DIR,
            'egg': migrations_dir,
        })

    os.chdir(os.path.join(settings.BASE_DIR, 'db'))
    if len(argv) != 0:
        if argv[0]=='all':
            for app in settings.APPS:
                migrate(app)
        else:
            migrate(argv[0])

    if len(argv) == 0 or argv[0]=='all':
        print("[ app ]")
        migrations_dir=lib.dirs(settings, format=["migrations"])

        os.system("echo y | orator migrate -c %(base)s/config/database.yml -p %(migrations_dir)s -d %(environment)s" % {
            'environment': environment,
            'base': settings.BASE_DIR,
            'migrations_dir': migrations_dir,
        })
    os.chdir(oldcwd)

