import sys
import os

brief = "create a test for controller"


def usage(argv0):
    print("Usage: {} generate test controller CONTROLLER_NAME METHOD [METHOD] [...]".format(argv0))
    sys.exit(1)


aliases = ['c']


def execute(argv, argv0, engine):
    import lib, inflection
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    from aioweb import settings

    sys.path.append(os.getcwd())
    if len(argv) < 2:
        usage(argv0)

    controller_name = inflection.camelize(argv[0]) + "Controller"
    controller_file_name = inflection.underscore(argv[0]) + ".py"

    methods = argv[1:]
    dest_file = os.path.join(lib.dirs(settings, format=["tests_controllers"]), controller_file_name)
    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
    template = lib.get_template("tests/controller.py", settings)

    if os.path.exists(dest_file):
        if lib.ask("{} already exists!\nDo you wanna replace it?".format(dest_file)) == 'n':
            print("Generation was aborted!")
            return

    print("creating {}".format(dest_file))

    with open(template, "r") as f:
        controller_code = f.read().replace("CLASS", controller_name).replace("CONTROLLER_NAME", controller_file_name[:-3])
        with open(dest_file, "w") as df:
            df.write(controller_code)

    for method in methods:
        engine["commands"]["generate"]["test"]["controller_method"]([argv[0], method], argv0, engine)
