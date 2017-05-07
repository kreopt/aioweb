import sys
import os

brief = "create a test for controller's method"


def usage(argv0):
    print("Usage: {} generate test controller_method CONTROLLER_NAME METHOD".format(argv0))
    sys.exit(1)


aliases = ['cm']


def execute(argv, argv0, engine):
    import lib, inflection, re
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    from aioweb import settings

    sys.path.append(os.getcwd())
    if len(argv) < 2:
        usage(argv0)

    controller_name = inflection.camelize(argv[0]) + "Controller"
    controller_file_name = inflection.underscore(argv[0]) + ".py"
    method_name = inflection.underscore(argv[1])

    controllers_dir = lib.dirs(settings, format=["tests_controllers"])
    dest_file = os.path.join(controllers_dir, controller_file_name)

    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
    template = lib.get_template("tests/controller_method.py", settings)

    if not os.path.exists(dest_file):
        print("Sorry but {} does not exist!".format(dest_file))
        return

    print("adding 'test_{}' to {}".format(method_name, dest_file))

    with open(template, "r") as f:
        method_code = f.read().replace("METHOD", method_name).replace("CLASS", controller_name).replace("CONTROLLER_NAME", controller_file_name[:-3])

    lib.insert_in_python(dest_file, ["class test_{}".format(controller_name)], method_code.split("\n"), in_end=True,
                         ignore_pass=True)

