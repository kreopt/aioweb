import sys
import os

brief = "test a controller"
aliases = ['c']


def usage(argv0):
    print("Usage: {} test controller CONTROLLER_NAME|--list|--help".format(argv0))
    sys.exit(1)


alias = ['c']


def execute(argv, argv0, engine):
    if not argv or '--help' in argv:
        usage(argv0)

    os.environ["AIOWEB_ENV"] = "test"
    environment = os.getenv("AIOWEB_ENV", "development")
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    import lib, inflection
    from aioweb import settings

    controllers_dir = lib.dirs(settings, format=["tests_controllers"])
    controller = inflection.underscore(argv[0])
    controller_path = os.path.join(controllers_dir, controller + ".py")

    if not controllers_dir:
        print("No model found!")
        sys.exit(0)

    if '--list' in argv:
        [print(m[:-3]) for m in os.listdir(controllers_dir) if m.endswith(".py") and not m.startswith("__")]

        sys.exit(0)
    test_file = os.path.join(controllers_dir, controller + ".py")
    if not os.path.exists(test_file):
        print("No such file: " + test_file)
        sys.exit(1)

    os.system("python3 " + test_file)
