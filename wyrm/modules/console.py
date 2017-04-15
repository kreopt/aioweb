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
        models_dir = lib.dirs(settings, app, ["models"], check=True)
        if not models_dir: continue
        models = [ model_file.replace(".py", '') for model_file in os.listdir(models_dir) \
                   if re.match(r"^[a-z0-9_]+\.py$", model_file) and model_file!="__init__.py"]
        # Import models
        for model in models:
            class_name = lib.names(model, ["class"])
            model_import = lib.get_import("models", model, app)
            try:
                m = importlib.import_module(model_import)
                exec("{0} = m.{0}".format(class_name) )
                local_vars[class_name] = locals()[class_name]
                print("from " + model_import + " import " + class_name)
            except: 
                print("WARNING: cannot import {}".format( model_import ))

    code.interact(local=local_vars, banner="You are welcome in the aioweb console!\n\n")

