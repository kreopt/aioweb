import sys
import os

brief = "describe me"


def usage(argv0):
    print("Usage: {} MODULE_FULL_NAME".format(argv0))
    sys.exit(1)


aliases = []


def execute(argv, argv0, engine):
    import lib, inflection
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    from aioweb import settings

    if len(argv) == 0:
        usage(argv0)


