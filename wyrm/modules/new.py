import os, sys
import shutil
aliases=["n"]
brief="create a new project"
def usage(argv0):
    print("Usage: {} new project_name [dirname]".format(argv0))

def execute(argv, argv0, engine):
    import lib

    if len(argv) == 0 or len(argv) > 2 or argv[0] in ['-h', '--help'] or argv[-1] in ['-h', '--help']:
        usage(argv0)
        sys.exit(1)
    name = argv[0]
    dirname= argv[-1]
    gen_path = lib.get_template("new")
    if not gen_path:
        print("ERROR: can't locate generator templates!")
        sys.exit(1)
    if os.path.exists(dirname):
        print("cleaning {}".format(os.path.abspath(dirname)))
        if os.listdir(dirname):
            rc = lib.ask("{} is not empty.\nDo you wanna empty this folder?".format(os.path.abspath(dirname)))
            if rc != 'y':
                print("Generation was aborted.")
                sys.exit(1)

        for entry in os.listdir(dirname):
            path = os.path.join(dirname, entry)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.unlink(path)
        print("coping files...")
        for entry in os.listdir(gen_path):
            src  = os.path.join(gen_path, entry)
            dest = os.path.join(dirname, entry)
            if os.path.isdir(src):
                shutil.copytree(src, dest)
            else:
                shutil.copy2(src, dest)
    else:
        print("coping files...")
        shutil.copytree(gen_path, dirname)

