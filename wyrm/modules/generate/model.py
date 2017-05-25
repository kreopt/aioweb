import sys
import os

brief = "create a new model with migration"


def usage(argv0):
    print("Usage: {} generate model MODEL_NAME [FIELD_NAME:FIELD_TYPE] [FIELD_NAME:FIELD_TYPE] [...]".format(argv0))
    sys.exit(1)


aliases = ['m']


def execute(argv, argv0, engine):
    import lib
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    from aioweb import settings

    sys.path.append(os.getcwd())

    if len(argv) == 0 or '-h' in argv or '--help' in argv or argv[0].startswith('-'):
        usage(argv0)

    additional_fields = lib.get_fields_from_argv(argv[1:], usage, argv0)

    migrations_dir, models_dir = lib.dirs(settings, format=["migrations", "models"])
    table, model_name, model_class = lib.names(argv[0], ["table", "model", "class"])

    migration_name = "create_{}_table".format(table)
    model_file = os.path.join(models_dir, "{}.py".format(model_name))
    rewrite = True
    if os.path.exists(model_file):
        if lib.ask("{} already exists. Do you wanna rewrite it?".format(model_file)) == 'n': rewrite = False
        if rewrite:
            print("delete " + model_file)
            os.unlink(model_file)

    if rewrite:
        os.system("orator make:model {} -p app/models".format(argv[0].capitalize()))

    rewrite = True
    try:
        rc = [f for f in os.listdir(migrations_dir) if migration_name in f]
    except FileNotFoundError:
        rc = []
    if len(rc) > 0:
        if lib.ask(
            "{} already exists.\nDo you wanna rewrite it?".format("db/migrations/" + rc[0])) == 'n': rewrite = False
        if rewrite:
            for f in rc:
                print("delete " + "db/migrations/" + f)
                os.unlink(os.path.join(migrations_dir, f))

    if rewrite:
        os.system("orator make:migration {} -p db/migrations/ -C -t {}".format(migration_name, table))
        file_name = os.path.join(migrations_dir,
                                 [f for f in sorted(os.listdir(migrations_dir)) if migration_name in f][-1])
        print("patching " + file_name)
        lib.insert_in_python(file_name, ["def up", "as table:"],
                             ["table.{}('{}').nullable()".format(tp, name) for tp, name in additional_fields],
                             in_end=True)
        print("patching " + model_file)
        fillable = "__fillable__ = [{}]".format(", ".join( ['"{}"'.format(name) for tp, name in additional_fields] ))
        print(fillable)
        lib.insert_in_python(model_file, ["class"],
                             [fillable] + ["# {}{} - {}".format(name, (25 - len(name)) * ' ', tp) for tp, name in additional_fields],
                             ignore_pass=True)

    print("generating factory")
    engine["commands"]["generate"]["test"]["factory"](argv, argv0, engine)
    engine["commands"]["generate"]["test"]["model"](argv[:1], argv0, engine)
