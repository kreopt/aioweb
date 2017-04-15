import sys
import os

brief="add a method to the controller"
def usage(argv0):
    print("Usage: {} generate controller_method CONTROLLER_NAME METHOD".format(argv0))
    sys.exit(1)

aliases=['cm']
def execute(argv, argv0, engine):
    import lib, inflection, re
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    from aioweb import settings

    sys.path.append( os.getcwd() )
    if len(argv) < 2:
        usage(argv0)
    route_name           = inflection.underscore(argv[0]) + '#' + inflection.underscore(argv[1])
    controller_name      = inflection.camelize(argv[0]) + "Controller"
    controller_file_name = inflection.underscore(argv[0]) + ".py"
    method_name          = inflection.underscore(argv[1])

    controllers_dir, configs_dir, views_dir = lib.dirs(settings, format=["controllers", "config", "views"])

    dest_file   = os.path.join( controllers_dir, controller_file_name )
    routes_file = os.path.join( configs_dir, "routes.py" )
    view_file   = os.path.join( views_dir, inflection.underscore(argv[0]) + "/" + method_name + ".html")

    os.makedirs( os.path.dirname(dest_file), exist_ok=True)
    template=lib.get_template("controllers/simple_controller_method.py") 

    if not os.path.exists( dest_file ):
        print("Sorry but {} does not exist!".format(dest_file))
        return

    print("adding '{}' to {}".format(method_name, dest_file ))

    with open(template, "r") as f: method_code=f.read().replace("METHOD", method_name)

    lib.insert_in_python(dest_file, ["class {}".format(controller_name)], method_code.split("\n"), in_end=True, ignore_pass=True)

    os.makedirs( os.path.dirname(view_file), exist_ok=True)
    if not os.path.exists(view_file):
        print("creating " + view_file)
        template=lib.get_template("controllers/view.html") 

        with open(template, "r") as f: view_code=f.read().replace("ROUTE_NAME", route_name)

        with open(view_file, "w") as f: f.write(view_code)
        

        
    with open(routes_file, "r") as f:
        if re.search(r"['\"]{}['\"]".format(route_name), f.read()):
            print("")
            return

    print("patching {}".format(routes_file ))
    lib.insert_in_python(routes_file, ["setup(router)"], ["router.get('{}')".format(route_name)], in_end=True)
    print("")

