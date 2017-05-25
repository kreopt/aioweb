import sys
import os

brief = "create a model and CRUD controller"


def usage(argv0):
    print("Usage: {} generate crud MODEL_NAME [FIELD_NAME:FIELD_TYPE] [FIELD_NAME:FIELD_TYPE] [...]".format(argv0))
    sys.exit(1)


aliases = []


def execute(argv, argv0, engine):
    import lib, inflection
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    from aioweb import settings

    if len(argv) == 0 or '-h' in argv or '--help' in argv:
        usage(argv0)

    engine["commands"]["generate"]["model"](argv, argv0, engine)
    engine["commands"]["generate"]["crud_controller"](argv, argv0, engine)



