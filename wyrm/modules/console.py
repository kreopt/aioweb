import sys
import os


brief="start the aioweb console"
aliases=["c", "shell"]

def execute(argv, argv0, engine):
    import lib, importlib, re
    import code
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    from aioweb import settings
    sys.path.append( settings.BASE_DIR )
    # Initialize Orator ORM
    lib.init_orator(settings)


    local_vars = {}
    print("")
    for app in settings.APPS + [None]:
        if app:
            models_dir = os.path.join( os.path.dirname(importlib.util.find_spec(app).origin), "models" )
        else:
            models_dir = os.path.join( settings.BASE_DIR, "app/models" )

        models = [ model_file.replace(".py", '') for model_file in os.listdir(models_dir) if model_file.endswith(".py") and model_file!="__init__.py"] \
            if os.path.exists( models_dir ) else []
        # Import models
        for model in models:
            if re.match(r"[a-zA-Z0-9_]+", model):
                class_name = lib.names(model, ["class"])
                if app:
                    model_import = "{}.models.{}".format(app, model)
                else:
                    model_import = "app.models.{}".format(model)
                try:
                    m = importlib.import_module(model_import)
                    exec("{0} = m.{0}".format(class_name) )
                    local_vars[class_name] = locals()[class_name]
                except: 
                    pass
                print("from " + model_import + " import " + class_name)

    code.interact(local=local_vars, banner="You are welcome in the aioweb console!\n\n")

