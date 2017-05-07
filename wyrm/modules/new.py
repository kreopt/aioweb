import os, sys
import shutil

aliases = ["n"]
brief = "create a new project"


def usage(argv0):
    print("Usage: {} new [module_name] dirname".format(argv0))


def execute(argv, argv0, engine):
    import lib

    if len(argv) == 0 or len(argv) > 2 or argv[0] in ['-h', '--help'] or argv[-1] in ['-h', '--help']:
        usage(argv0)
        sys.exit(1)
    name = argv[0]
    dirname = argv[-1]
    appdir  = dirname
    if len(argv) >= 2:
        appdir = os.path.join( dirname, name )

    gen_path = lib.get_template("new")
    if not gen_path:
        print("ERROR: can't locate generator templates!")
        sys.exit(1)

    if os.path.exists(appdir):
        print("cleaning {}".format(os.path.abspath(appdir)))
        if os.listdir(appdir):
            rc = lib.ask("{} is not empty.\nDo you wanna empty this folder?".format(os.path.abspath(appdir)))
            if rc != 'y':
                print("Generation was aborted.")
                sys.exit(1)

        for entry in os.listdir(appdir):
            path = os.path.join(appdir, entry)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.unlink(path)
        print("coping files...")
        for entry in os.listdir(gen_path):
            src = os.path.join(gen_path, entry)
            dest = os.path.join(appdir, entry)
            if os.path.isdir(src):
                shutil.copytree(src, dest)
            else:
                shutil.copy2(src, dest)
    else:
        if appdir != dirname:
            os.makedirs(dirname, exist_ok=True)
        print("coping files...")
        shutil.copytree(gen_path, appdir)

    os.makedirs( os.path.join(appdir, "wyrm/generators"), exist_ok=True)
    os.makedirs( os.path.join(appdir, "wyrm/modules"), exist_ok=True)

    if appdir != dirname:
        print("patching setup.py")
        print(lib.get_template("setup.py"))
        shutil.copy2(lib.get_template("setup.py"), os.path.join(dirname, "setup.py") )
        with open(os.path.join(dirname, "setup.py"), "r") as f: setup_py = f.read().replace("APP_NAME", name)
        with open(os.path.join(dirname, "setup.py"), "w") as f: f.write( setup_py )
