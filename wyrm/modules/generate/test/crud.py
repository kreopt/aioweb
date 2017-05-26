import sys
import os

brief = "create a test for crud controller"


def usage(argv0):
    print("Usage: {} generate test crud MODEL_NAME [FIELD_NAME:FIELD_TYPE] [FIELD_NAME:FIELD_TYPE] [...]".format(argv0))
    sys.exit(1)


aliases = []


def execute(argv, argv0, engine):
    import lib, inflection
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    from aioweb import settings

    if len(argv) == 0 or '-h' in argv or '--help' in argv:
        usage(argv0)

    additional_fields = lib.get_fields_from_argv(argv[1:], usage, argv0)

    tests_dir = lib.dirs(settings, format=["tests_controllers"])
    table, model_name, model_class, controller_class = lib.names(argv[0], ["table", "model", "class", 'crud_class'])

    controller_file_name = "{}.py".format(table)
    dest_file = os.path.join(tests_dir, controller_file_name)

    test_field = "strawberry_field"
    if len(additional_fields) > 0: test_field = additional_fields[0][1]

    replacements= {
                    'MODEL': model_name, 
                    'MODEL_CLASS': model_class,
                    'CONTROLLER_CLASS': controller_class,
                    'TABLE': table,
                    'TEST_FIELD': test_field,
                  }
    crud_test_code = lib.read_template("tests/crud.py", settings=settings, replacements=replacements)
    print("generating {}...".format(dest_file))
    os.makedirs(tests_dir, exist_ok=True)
    with open(dest_file, "w") as f:
        f.write(crud_test_code)

