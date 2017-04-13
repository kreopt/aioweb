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

    if '-h' in argv or '--help' in argv:
        usage(argv0)
    oldcwd = os.getcwd()
    try:
        os.mkdir(os.path.join(settings.BASE_DIR, 'db'))
    except: pass

    os.chdir(os.path.join(settings.BASE_DIR, 'db'))

    for app in settings.APPS:
        print("[ %s ]" % app)
        print("%(egg)s/migrations/" % {'egg': os.path.dirname(importlib.util.find_spec(app).origin)})
        os.system("orator migrate:status -c %(base)s/config/database.yml -p %(egg)s/migrations/" % {
            'base': settings.BASE_DIR,
            'egg': os.path.dirname(importlib.util.find_spec(app).origin)
        })
    print("[ app ]")

    os.system("orator migrate:status -c %(base)s/config/database.yml -p %(base)s/db/migrations/" % {
        'base': settings.BASE_DIR
    })
    os.chdir(oldcwd)


