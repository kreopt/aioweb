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

    oldcwd = os.getcwd()
    try:
        os.mkdir(os.path.join(settings.BASE_DIR, 'db'))
    except: pass

    if len(argv) != 0 and argv[0] not in settings.APPS+["all"]:
        print("ERROR: can't locate the {} app".format(argv[0]))
        print("available apps: {}".format(", ".join(settings.APPS)))
        usage(argv0)

    def migrate(app):
        print("[ %s ]" % app)
        print("%(egg)s/migrations/" % {'egg': os.path.dirname(importlib.util.find_spec(app).origin)})
        os.system("orator migrate -c %(base)s/config/database.yml -p %(egg)s/migrations/" % {
            'base': settings.BASE_DIR,
            'egg': os.path.dirname(importlib.util.find_spec(app).origin)
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

        os.system("orator migrate -c %(base)s/config/database.yml -p %(base)s/db/migrations/" % {
            'base': settings.BASE_DIR
        })
    os.chdir(oldcwd)

