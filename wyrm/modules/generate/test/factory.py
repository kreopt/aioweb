import sys
import os

brief="create a factory"
def usage(argv0):
    print("Usage: {} generate factory MODEL_NAME [FIELD_NAME:FIELD_TYPE] [FIELD_NAME:FIELD_TYPE] [...]".format(argv0))
    sys.exit(1)

def execute(argv, argv0, engine):
    if not argv:
        usage(argv0)

    import lib
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    from aioweb import settings

    table, model_name, model_class = lib.names(argv[0], ["table", "model", "class"])
    additional_fields = lib.get_fields_from_argv(argv[1:], usage, argv0)
    if not additional_fields: additional_fields = [("string","somefield")]

    os.makedirs(os.path.join(settings.BASE_DIR, 'tests/factories/'), exist_ok=True)
    dest_path = os.path.join(settings.BASE_DIR, 'tests/factories/{}_factory.py'.format(table))
    if os.path.exists(dest_path):
        if lib.ask(dest_path + " exists\nDo You wanna rewrite it?") == 'n':
           print("factory generation cancelled")
           return 
    template=lib.get_template("tests/factory.py") 
    with open(template, "r") as f:
        print("generating " + dest_path)
        content=f.read().replace("MODEL", model_name).replace("CLASS", model_class).replace("TABLE", table)
        with open(dest_path, "w") as df:
            df.write(content)
        lib.insert_in_python( dest_path, ["import"], ['from app.models.{} import {}'.format(model_name, model_class)])
        lib.insert_in_python( dest_path, ["return"], map(lambda prm: '    "{}": None, '.format(prm[1]), additional_fields) )
        



