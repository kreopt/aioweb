import sys
import os

brief = "delete a test for controller"


def usage(argv0):
    print("Usage: {} destroy test controller CONTROLLER_NAME".format(argv0))
    sys.exit(1)


aliases = ['c']


def execute(argv, argv0, engine):
    import lib, shutil, inflection
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    from aioweb import settings

    sys.path.append(os.getcwd())
    if len(argv) == 0 or '-h' in argv or '--help' in argv:
        usage(argv0)

    controllers_dir = lib.dirs(settings, format=["tests_controllers"])
    controller = inflection.underscore(argv[0])
    controller_path = os.path.join(controllers_dir, controller + ".py")

    if os.path.exists(controller_path):
        print("removing " + controller_path)
        os.unlink(controller_path)

