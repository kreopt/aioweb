import sys
import os

brief = "create a new seed"


def usage(argv0):
    print(
        "Usage: {} generate seed SEED_NAME".format(
            argv0))
    sys.exit(1)


aliases = ['sd']


def execute(argv, argv0, engine):
    import lib
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    from aioweb import settings

    sys.path.append(os.getcwd())

    if len(argv) < 1 or '-h' in argv or '--help' in argv:
        usage(argv0)

    seeds_dir = lib.dirs(settings, format=["seeds"])

    seed_name = argv[0]

    try:
        seeds = [os.path.join(seeds_dir, f) for f in os.listdir(seeds_dir) if seed_name in f]
    except FileNotFoundError:
        seeds = []
    rc = None
    for m in seeds:
        if rc not in ['a', 'all']: rc = lib.ask(
            "\n{} already exists.\nDo you wanna remove it before create migration?".format(m),
            ['y', 'n', 'e', 'exit', 'all', 'a', 'skip all'])
        if rc in ['skip all']:
            break
        if rc in ['e', 'exit']:
            print("migration aborted")
            sys.exit(1)

        if rc in ['a', 'y', 'all']:
            print("delete " + m)
            os.unlink(m)

    os.system("orator make:seed {} -p {}".format(seed_name, seeds_dir))
