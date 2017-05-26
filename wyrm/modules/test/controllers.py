import sys
import os

brief = "test all controllers"


def usage(argv0):
    print("Usage: {} test controllers [--list|--help]".format(argv0))
    sys.exit(1)


aliases = ['cs']


def execute(argv, argv0, engine):
    if '--help' in argv or '-h' in argv:
        usage(argv0)

    os.environ["AIOWEB_ENV"] = "test"
    environment = os.getenv("AIOWEB_ENV", "development")
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    import lib, inflection
    from aioweb import settings
    
    tests_dir = lib.dirs(settings, format=["tests_controllers"], check=True)
    if not tests_dir:
        print("No controller found!")
        sys.exit(0)

    controllers = [m[:-3] for m in os.listdir(tests_dir) if m.endswith(".py") and not m.startswith("__")]
    if '--list' in argv:
        [print(m[:-3]) for m in os.listdir(tests_dir) if m.endswith(".py") and not m.startswith("__")]
        sys.exit(0)

    for ctrl in controllers:
        print(ctrl)
        test_file = os.path.join(tests_dir, ctrl + ".py")
        print("testing " + ctrl)
        rc = None
        if os.system("python3 " + test_file) != 0 and rc != 'a':
            rc = lib.ask("Do You wanna continue?", ['y', 'n', 'a'])
            if rc == 'n': sys.exit(1)

    


