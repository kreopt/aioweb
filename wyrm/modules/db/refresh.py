import sys
import os

brief="reset and re-run all datebase migrations"
aliases=[]
def usage(argv0):
    print("Usage: {} db refresh".format(argv0))
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
    os.makedirs(os.path.join(settings.BASE_DIR, 'db'), exist_ok=True)

    os.chdir(os.path.join(settings.BASE_DIR, 'db'))

    migrations_dir=lib.dirs(settings, format=["migrations"], check=True)
    engine["commands"]["db"]["reset"](argv, argv0, engine)
    engine["commands"]["db"]["migrate"](argv, argv0, engine)
    #os.system("orator migrate:refresh -c %(base)s/config/database.yml -p %(egg)s -d %(environment)s -n" % {
    #    'environment': environment,
    #    'base': settings.BASE_DIR,
    #    'egg': migrations_dir,
    #})
    os.chdir(oldcwd)




