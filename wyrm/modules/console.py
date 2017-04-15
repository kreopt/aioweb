import sys
import os


brief="start the aioweb console"
aliases=["c", "shell"]
def execute(argv, argv0, engine):
    import lib, importlib, re, yaml
    import code
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    from aioweb import settings
    # Initialize Orator ORM
    sys.path.append( settings.BASE_DIR )
    with open(os.path.join( settings.BASE_DIR, "config/database.yml"), "r") as f:
        dbconfig=yaml.load( f.read() )
        dbconfig = dbconfig["databases"]
        environment = os.getenv("AIOWEB_ENV", dbconfig["default"])
        dbconfig["default"] = environment
        if dbconfig[environment]["driver"] == "sqlite":
            dbconfig[environment]["database"]=os.path.join( settings.BASE_DIR, "db/{}".format(dbconfig[environment]["database"]) )
    from orator import DatabaseManager
    from orator import Model

    Model.set_connection_resolver( DatabaseManager(dbconfig) )


    models_dir = os.path.join( settings.BASE_DIR, "app/models" )
    models = [ model_file.replace(".py", '') for model_file in os.listdir(models_dir) if model_file.endswith(".py") and model_file!="__init__.py"] \
        if os.path.exists( models_dir ) else []
    local_vars = {}
    print("")
    # Import models
    for model in models:
        if re.match(r"[a-zA-Z0-9_]+", model):
            class_name = lib.names(model, ["class"])
            model_import = "app.models.{}".format(model)
            try:
                m = importlib.import_module(model_import)
                exec("{0} = m.{0}".format(class_name) )
            except: 
                pass
            finally:
                local_vars[class_name] = locals()[class_name]
            print("from " + model_import + " import " + class_name)

    code.interact(local=local_vars, banner="You are welcome in the aioweb console!\n\n")

