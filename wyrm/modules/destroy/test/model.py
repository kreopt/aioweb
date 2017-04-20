import sys
import os

brief="delete a model test"
def usage(argv0):
    print("Usage: {} destroy test model MODEL_NAME".format(argv0))
    sys.exit(1)

aliases=['m']

def execute(argv, argv0, engine):
    import lib, re
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    from aioweb import settings
    if not argv:
        usage(argv0)

    model_name = lib.names(argv[0], ["model"])
    dest_path = os.path.join( lib.dirs(settings, format=["tests"]), "models/" + model_name + ".py" )

    if os.path.exists(dest_path):
        print("removing " + dest_path)
        os.unlink(dest_path)



