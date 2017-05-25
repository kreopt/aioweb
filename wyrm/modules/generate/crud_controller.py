import sys
import os

brief = "create a new CRUD controller"


def usage(argv0):
    print("Usage: {} generate crud_controller MODEL_NAME [FIELD_NAME:FIELD_TYPE] [FIELD_NAME:FIELD_TYPE] [...]".format(argv0))
    sys.exit(1)


aliases = []

def execute(argv, argv0, engine):
    import lib, inflection, re
    from aioweb import settings

    if len(argv) == 0 or '-h' in argv or '--help' in argv:
        usage(argv0)
    additional_fields = lib.get_fields_from_argv(argv[1:], usage, argv0)
    controllers_dir, models_dir, views_dir,configs_dir = lib.dirs(settings, format=["controllers", "models", "views", "config"])
    table, model_name, model_class, controller_class = lib.names(argv[0], ["table", "model", "class", 'crud_class'])
    controller_file = os.path.join(controllers_dir, "{}.py".format(table))
    views_dir= os.path.join(views_dir, table)
    routes_file = os.path.join(configs_dir, "routes.py")

    rewrite=False
    replacements= {
                    'MODEL': model_name, 
                    'MODEL_CLASS': model_class,
                    'CONTROLLER_CLASS': controller_class,
                    'TABLE': table,
                    'MODEL_FIELD_NAMES': ', '.join(list(map(lambda type_name: '"' + type_name[1] + '"', additional_fields))),
                  }
    controller_code = lib.read_template("crud/controller.py", settings=settings, replacements=replacements)
    os.makedirs(controllers_dir, exist_ok=True)
    if os.path.exists(controller_file):
        if lib.ask(controller_file + " already exists.\nDo you wanna rewrite it?") == 'n':
            sys.exit(1)
    print("creating {}...".format(controller_file))

    with open(controller_file, "w") as f: f.write(controller_code)
    with open(routes_file, "r") as f:
        if not re.search(r"['\"]{}['\"]".format(table), f.read()):
            print("patching {}".format(routes_file))
            lib.insert_in_python(routes_file, ["setup(router)"], ["router.resource('{}', '{}')".format(table, table)], in_end=True)
    print("")
    if os.path.exists(views_dir):
        if lib.ask(views_dir + "/ already exists.\nDo you wanna wipe out it?") == 'n':
            sys.exit(1)

    form_fields = ""
    for tp, name in additional_fields:
        form_fields+='<div class="field">\n'
        form_fields+='  <label>{}\n'.format(name)
        form_fields+='    <input'
        if tp in ['decimal', 'double', 'integer', 'big_integer', 'float']:
           form_fields += ' type="number" '
        else:
           form_fields += ' type="text"   '
        form_fields+='name="{}[{}]" '.format(model_name, name)
        form_fields+= '{% if model.' + name + ' != None %} ' + 'value="{{ model.' + name + ' }}" ' + '{% endif %}'

        form_fields+='>' + "</input>"
        form_fields+="\n"
        form_fields+='  </label>\n</div>'
    replacements={
                    'MODEL': model_name,
                    'TABLE': table,
                    'FORM_FIELDS': form_fields,
                 }
    os.makedirs(views_dir, exist_ok=True)
    for view_name in ["index.html", "get.html", "form.html", "edit_page.html", "add.html", "add_page.html", "edit.html"]:
        view_file = os.path.join(views_dir, view_name)
        print("creating {}...".format(view_file))
        view_code = lib.read_template("crud/{}".format(view_name), settings=settings, replacements=replacements)
        with open(view_file, "w") as f: f.write(view_code)


