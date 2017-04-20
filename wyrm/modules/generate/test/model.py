import sys
import os

brief="create an unittest for model"
def usage(argv0):
    print("Usage: {} generate test model MODEL_NAME".format(argv0))
    sys.exit(1)

alias=['m']

def execute(argv, argv0, engine):
    if not argv:
        usage(argv0)

    import lib
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    from aioweb import settings

    table, model_name, model_class = lib.names(argv[0], ["table", "model", "class"])
    dest_path = os.path.join( lib.dirs(settings, format=["tests"]), "models/" + model_name + ".py" )

    os.makedirs( os.path.dirname( dest_path ), exist_ok=True )
    if os.path.exists(dest_path):
        if lib.ask("{} already exists!\nDo You wanna rewrite it?".format(dest_path))=='n':
            return

    template=lib.get_template("tests/model.py") 
    with open(template, "r") as f:
        print("generating " + dest_path)
        content=f.read().replace("MODEL", model_name).replace("CLASS", model_class).replace("TABLE", table)
        with open(dest_path, "w") as df:
            df.write(content)
