import sys
import os

brief="create a new model with migration"
def usage(argv0):
    print("Usage: {} generate model MODEL_NAME [FIELD_NAME:FIELD_TYPE] [FIELD_NAME:FIELD_TYPE] [...]".format(argv0))
    sys.exit(1)

additional_fields=[]
def execute(argv, argv0, engine):
    import lib
    import inflection
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    sys.path.append( os.getcwd() )
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

    def migration_patch(lines, n):
        for i, line in enumerate(lines[n+1:]):
            if line.strip():
                indent = lib.indent(line)
                for tp,name in additional_fields:
                    lines.insert(n+i+1, indent+"table.{}('{}')\n".format(tp, name))
                break
        return lines

    table = inflection.tableize(argv[0])
    migration_name = "create_{}_table".format(table)
    model_name=inflection.singularize( table )
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
    rc = [f for f in os.listdir( "db/migrations" ) if migration_name in f]
    if len(rc) > 0:
        if lib.ask("{} already exists. Do you wanna rewrite it?".format("db/migrations/"+rc[0])) == 'n': rewrite = False
        if rewrite:
            for f in rc:
                print("delete " + "db/migrations/" + f)
                os.unlink("db/migrations/" + f)

    if rewrite:
        os.system("orator make:migration {} -p db/migrations/ -C -t {}".format(migration_name, table))
        file_name = "db/migrations/" + [f for f in os.listdir( "db/migrations" ) if migration_name in f][0]
        print("patching " + file_name)
        lib.patch(file_name, ["def up", "as table:"], migration_patch)
        
    

