import sys
import os

brief = "import migrations form apps"


def usage(argv0):
    print("Usage: {} db import [app_name|all]".format(argv0))
    sys.exit(1)


aliases = ['i']


def execute(argv, argv0, engine):
    import lib, importlib, re, shutil
    from datetime import datetime
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    from aioweb import settings
    sys.path.append(os.getcwd())

    if '-h' in argv or '--help' in argv or not argv:
        usage(argv0)

    if argv[0] not in settings.APPS + ["all"]:
        print("ERROR: can't locate the {} app".format(argv[0]))
        print("available apps: {}".format(", ".join(settings.APPS)))
        usage(argv0)

    dest_dir = lib.dirs(settings, format=["migrations"])
    os.makedirs(dest_dir, exist_ok=True)

    def import_migrations_from_app(app):
        migrations_dir = lib.dirs(settings, app=app, format=["migrations"], check=True)
        if not migrations_dir: return
        print("[ %s ]" % app)
        existant_migrations = []
        for m in sorted(os.listdir(dest_dir)):
            if not m.startswith('_') and m.endswith('.py'):
                mp = os.path.join(dest_dir, m)
                with open(mp) as f:
                    if "# {} module".format(app) in f.read():
                        existant_migrations.append(mp)

        if existant_migrations:
            rc = lib.ask("The migrations for {} alerady installed.\nDo You wanna remove its?".format(app))
            if rc == 'n':
                return
            for m in existant_migrations:
                print("removing " + m)
                os.unlink(m)
            print("")

        migrations = [(os.path.join(migrations_dir, m), re.sub(r"^[\d_]+", "", m)[:-3]) for m in
                      sorted(os.listdir(migrations_dir)) if not m.startswith('_') and m.endswith('.py')]
        for path, name in migrations:
            ts = datetime.utcnow().strftime("%Y_%m_%d_%H%M%S%f")
            dest_file = os.path.join(dest_dir, ts + "_" + name + ".py")
            print("creating " + dest_file)
            shutil.copy2(path, dest_file)
            lib.insert_in_python(dest_file, ["from"], ["# {} module. please dont remove this line".format(app)],
                                 in_end=True, ignore_pass=True)

    if argv[0] == 'all':
        for app in settings.APPS:
            import_migrations_from_app(app)
    else:
        import_migrations_from_app(argv[0])
