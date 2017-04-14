import sys
import os

brief="delete the model and all model's migrations"
def usage(argv0):
    print("Usage: {} destroy model MODEL_NAME".format(argv0))
    sys.exit(1)

aliases=['m']
def execute(argv, argv0, engine):
    import lib, re
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    from aioweb import settings
    migrations_dir = os.path.abspath( os.path.join(settings.BASE_DIR, 'db/migrations') )

    sys.path.append( os.getcwd() )

    table, model_name = lib.names(argv[0], ["table", "model"])
    migration_name = "create_{}_table".format(table)
    model_file="app/models/{}.py".format(model_name)

    if os.path.exists(model_file):
        print("delete " + model_file)
        os.unlink(model_file)

    try: rc = [os.path.join(migrations_dir, f) for f in os.listdir( migrations_dir ) if os.path.isfile( os.path.join(migrations_dir, f) ) ]
    except FileNotFoundError: rc=[]
    for file_path in rc:
        sr=None
        with open(file_path, "r") as f:
            sr=re.search(r"schema\.\w+\(\s*['\"]{}['\"]".format(table), f.read())
        if sr:
            print("delete " + file_path)
            os.unlink( file_path )
    print("destroying factory")
    engine["commands"]["destroy"]["test"]["factory"](argv, argv0, engine)

