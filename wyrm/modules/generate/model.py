import sys
import os

brief="create a new model with migration"
def usage(argv0):
    print("Usage: {} generate model MODEL_NAME [FIELD_NAME:FIELD_TYPE] [FIELD_NAME:FIELD_TYPE] [...]".format(argv0))
    sys.exit(1)

aliases=['m']
def execute(argv, argv0, engine):
    import lib
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    from aioweb import settings
    migrations_dir = os.path.abspath( os.path.join(settings.BASE_DIR, 'db/migrations') )

    sys.path.append( os.getcwd() )

    additional_fields=[]
    if len(argv) == 0 or '-h' in argv or '--help' in argv or argv[0].startswith('-'):
        usage(argv0)
    for field in argv[1:]:
        try:
            field_name, field_type = field.split(':')
            if not field_type:
                usage(argv0)
        except:
            usage(argv0)
        additional_fields.append( (field_type, field_name) )

    table, model_name, model_class = lib.names(argv[0], ["table", "model", "class"])
    migration_name = "create_{}_table".format(table)
    model_file="app/models/{}.py".format(model_name)
    rewrite = True
    if os.path.exists(model_file):
        if lib.ask("{} already exists. Do you wanna rewrite it?".format(model_file)) == 'n': rewrite = False
        if rewrite:
            print("delete " + model_file)
            os.unlink(model_file)

    if rewrite:
        os.system("orator make:model {} -p app/models".format(argv[0].capitalize()))

    rewrite = True
    try: rc = [f for f in os.listdir( migrations_dir ) if migration_name in f]
    except FileNotFoundError: rc=[]
    if len(rc) > 0:
        if lib.ask("{} already exists.\nDo you wanna rewrite it?".format("db/migrations/"+rc[0])) == 'n': rewrite = False
        if rewrite:
            for f in rc:
                print("delete " + "db/migrations/" + f)
                os.unlink( os.path.join( migrations_dir,  f) )

    if rewrite:
        os.system("orator make:migration {} -p db/migrations/ -C -t {}".format(migration_name, table))
        file_name = os.path.join( migrations_dir, [f for f in sorted( os.listdir(migrations_dir) ) if migration_name in f][-1] )
        print("patching " + file_name)
        lib.insert_in_python(file_name, ["def up", "as table:"], ["table.{}('{}').nullable()".format(tp, name) for tp,name in additional_fields ], in_end=True)
        print("patching " + model_file)
        lib.insert_in_python(model_file, ["class"], ["# {}{} - {}".format(name, (25-len(name) )*' ', tp) for tp,name in additional_fields ], ignore_pass=True)

