import sys
import os

brief="delete the model and all model's migrations"
def usage(argv0):
    print("Usage: {} destroy factory MODEL_NAME".format(argv0))
    sys.exit(1)

def execute(argv, argv0, engine):
    import lib, re
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    from aioweb import settings
    if not argv:
        usage(argv0)

    table = lib.names(argv[0], ["table"])
    factory_path = os.path.abspath( os.path.join(settings.BASE_DIR, 'tests/factories/{}_factory.py'.format(table) ) )
    if os.path.exists(factory_path):
        print("removing " + factory_path)
        os.unlink(factory_path)


