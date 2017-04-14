import sys
import os

brief="create a new migration"
def usage(argv0):
    print("Usage: {} generate migration MODEL_NAME MIGRATION_NAME [FIELD_NAME:FIELD_TYPE] [FIELD_NAME:FIELD_TYPE] [...]".format(argv0))
    sys.exit(1)

aliases=['mg']
def execute(argv, argv0, engine):
    import lib
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    from aioweb import settings
    migrations_dir = os.path.abspath( os.path.join(settings.BASE_DIR, 'db/migrations') )

    sys.path.append( os.getcwd() )
    if len(argv) <= 1 or '-h' in argv or '--help' in argv:
        usage(argv0)
    additional_fields = lib.get_fields_from_argv(argv[2:], usage, argv0)

    table, model_name, model_class = lib.names(argv[0], ["table", "model", "class"])
    migration_name = argv[1]
    model_file="app/models/{}.py".format(model_name)
    if not os.path.exists(model_file):
        if lib.ask("{} does not exists.\nDo you wanna continue?".format(model_file)) == 'n':
            print("migration aborted")
            sys.exit(1)

    try: migrations = [os.path.join(migrations_dir, f) for f in os.listdir( migrations_dir ) if migration_name in f]
    except FileNotFoundError: migrations=[]
    rc=None
    for m in migrations:
        if rc not in ['a', 'all']: rc= lib.ask("\n{} already exists.\nDo you wanna remove it before create migration?".format(m), ['y', 'n', 'e', 'exit', 'all', 'a', 'skip all'])
        if rc in ['skip all']:
            break
        if rc in ['e', 'exit']:
            print("migration aborted")
            sys.exit(1)
        
        if rc in ['a','y', 'all']:
            print("delete " + m )
            os.unlink( m )

    os.system("orator make:migration {} -p {} -t {}".format(migration_name, migrations_dir, table))
    file_name = os.path.join( migrations_dir, [f for f in sorted( os.listdir(migrations_dir) ) if migration_name in f][-1] )
    print("patching " + file_name)
    lib.insert_in_python(file_name, ["def up", "as table:"], ["table.{}('{}').nullable()".format(tp, name) for tp,name in additional_fields ] )
    lib.insert_in_python(file_name, ["def down", "as table:"], ["table.drop_column('{}')".format(name) for tp,name in additional_fields ] )
    if os.path.exists(model_file):
        print("patching " + model_file)
        lib.insert_in_python(model_file, ["class"], ["# {}{} - {}".format(name, (25-len(name) )*' ', tp) for tp,name in additional_fields ], ignore_pass=True)

