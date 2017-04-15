import sys
import os

brief="rollback the database"
def usage(argv0):
    print("Usage: {} db rollback [app_name]".format(argv0))
    sys.exit(1)

aliases=['r']
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
    if len(argv) != 0 and argv[0] not in settings.APPS:
        print("ERROR: can't locate the {} app".format(argv[0]))
        print("available apps: {}".format(", ".join(settings.APPS)))
        usage(argv0)

    os.chdir(os.path.join(settings.BASE_DIR, 'db'))
    if len(argv) != 0:
        app = argv[0]
        migrations_dir=lib.dirs(settings, app=app, format=["migrations"], check=True)
        print("[ %s ]" % app)
        if migrations_dir:
            print(migrations_dir)
            os.system("echo y | orator migrate:rollback -c %(base)s/config/database.yml -p %(egg)s -d %(environment)s" % {
                'environment': environment,
                'base': settings.BASE_DIR,
                'egg': migrations_dir,
            })
        else:
            print("No migrations found")
    else:
        print("[ app ]")
        migrations_dir=lib.dirs(settings, format=["migrations"], check=True)
        if migrations_dir:
            os.system("echo y | orator migrate:rollback -c %(base)s/config/database.yml -p %(egg)s -d %(environment)s" % {
                'environment': environment,
                'base': settings.BASE_DIR,
                'egg': migrations_dir,
            })
        else:
            print("No migrations found")
    os.chdir(oldcwd)

