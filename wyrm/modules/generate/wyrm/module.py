import sys
import os

brief = "create a new wyrm module"


def usage(argv0):
    print("Usage: {} generate wyrm module [COLLECTION_NAME [COLLECTION_NAME..]] MODULE_NAME".format(argv0))
    sys.exit(1)


aliases = ['m']


def execute(argv, argv0, engine):
    import lib, inflection
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    from aioweb import settings

    if len(argv) == 0:
        usage(argv0)
    module_full_path = argv
    chase = engine["commands"]
    for i,m in enumerate(module_full_path):
        rc= chase.get(m)
        if not rc:
            chase=None
            break
        elif type(rc) == str:
            module_full_path[i] =rc
            chase=chase.get(rc)
        else:
            chase=rc
    dest_file=os.path.join("wyrm", "modules", *module_full_path) + ".py"

    if type(chase)==dict:
        print("CONFLICT: " + '"' + ' '.join(module_full_path) + '" is a module collection!' )
        sys.exit(1)

    elif os.path.exists(dest_file):
        rc=lib.ask(dest_file + " already exists!\nDo You wanna rewrite it???")
        if rc=='n': sys.exit(0)

    elif callable(chase):
        rc=lib.ask("This module already exists! Do You wanna replace it?")
        if rc=='n': sys.exit(0)

    print("generating " + '"' + ' '.join(module_full_path) + '"' )
    os.makedirs(os.path.dirname(dest_file), exist_ok=True)

    template = lib.get_template("wyrm/module.py", settings)
    with open(template, "r") as f:
        module_code = f.read().replace("MODULE_FULL_NAME", ' '.join(module_full_path))
        with open(dest_file, "w") as df:
            df.write(module_code)
    
