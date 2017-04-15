import sys
import os

brief="delete the migration"
def usage(argv0):
    print("Usage: {} destroy migration [MODEL_NAME] MIGRATION_NAME".format(argv0))
    sys.exit(1)

aliases=['mg']
def execute(argv, argv0, engine):
    import lib
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    from aioweb import settings
    migrations_dir = lib.dirs(settings, format=["migrations"])

    sys.path.append( os.getcwd() )
    if len(argv) == 0 or '-h' in argv or '--help' in argv:
        usage(argv0)

    migration_name = argv[ 0 if len(argv) == 1 else 1 ]

    try: migrations = [os.path.join(migrations_dir, f) for f in os.listdir( migrations_dir ) if migration_name in f]
    except FileNotFoundError: migrations=[]
    for m in migrations:
        print("delete " + m )
        os.unlink( m )



