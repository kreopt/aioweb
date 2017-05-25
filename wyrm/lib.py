import os
import sys
import re
import importlib
import yaml
import inflection

vanila_dir = "share/aioweb/generators"
search_paths = [
    os.path.join(os.path.expanduser('~'), '.local'),
    '/usr/local/',
    '/usr/'
]


# def always_say_yes
# def always_say_no
# def ask
# def names
# def dirs
# def get_import
# def get_template
# def read_template
# def insert_in_python
# def indent

def locate_file(fname):
    for search_path in search_paths:
        path = os.path.join(search_path, fname)
        if os.path.exists(path):
            return path
    return None


def get_dbconfig(settings):
    with open(os.path.join(settings.BASE_DIR, "config/database.yml"), "r") as f:
        dbconfig = yaml.load(f.read())
        dbconfig = dbconfig["databases"]
        environment = os.getenv("AIOWEB_ENV", dbconfig["default"])
        dbconfig["default"] = environment
        if dbconfig[environment]["driver"] == "sqlite":
            dbconfig[environment]["database"] = os.path.join(settings.BASE_DIR,
                                                             "db/{}".format(dbconfig[environment]["database"]))
        return dbconfig


def init_orator(settings):
    import yaml
    from orator import DatabaseManager
    from orator import Model
    dbconfig = get_dbconfig(settings)

    if Model.get_connection_resolver():
        Model.get_connection_resolver().disconnect()
    Model.set_connection_resolver(DatabaseManager(dbconfig))


answer = None


def always_say_yes():
    global answer
    answer = 'y'


def always_say_no():
    global answer
    answer = 'n'


def ask(question, answers=["y", "n"]):
    global answer
    while True:
        print(question + " [" + ",".join(answers) + "]")
        rc = answer if answer and answer in answers else sys.stdin.readline().strip().lower()
        if rc in answers:
            return rc
        else:
            print("You bastard gimme a correct answer")


def names(word, format=[]):
    ret = {}
    ret["table"] = inflection.tableize(word)
    ret["model"] = inflection.singularize(ret["table"])
    ret["class"] = inflection.camelize(ret["model"])
    ret["crud_class"] = inflection.camelize( ret["table"] + "_controller")
    if not format:
        return ret
    ret = [ret[k] for k in format]
    return ret[0] if len(ret) == 1 else ret


def dirs(settings, app=None, format=[], check=False):
    base_dir = os.path.dirname(importlib.util.find_spec(app).origin) if app  else settings.BASE_DIR
    if app: print(base_dir)
    ret = {}
    ret["generators"] = os.path.join(base_dir, "wyrm/generators")
    ret["config"] = os.path.join(base_dir, "config")
    ret["tests"] = os.path.join(base_dir, "tests")
    ret["factories"] = os.path.join(base_dir, "tests/factories")
    ret["models"] = os.path.join(base_dir, "app/models")
    ret["controllers"] = os.path.join(base_dir, "app/controllers")
    ret["views"] = os.path.join(base_dir, "app/views")
    ret["migrations"] = os.path.join(base_dir, "db/migrations")
    ret["seeds"] = os.path.join(base_dir, "db/seeds")
    ret["tests_models"] = os.path.join(base_dir, "tests/models") if not app else None
    ret["tests_controllers"] = os.path.join(base_dir, "tests/controllers") if not app else None
    if check:
        for k in ret.keys():
            if ret[k] and not os.path.exists(ret[k]):
                ret[k] = None
    if not format:
        return ret
    ret = [ret[k] for k in format]
    return ret[0] if len(ret) == 1 else ret


def get_import(category, component, app=None):
    return ("{}.app".format(app) if app else "app") + ".{}.{}".format(category, component)


def get_template(subpath, settings=None):
    if settings:
        path = os.path.join(dirs(settings, format=["generators"]), subpath)
        if os.path.exists(path):
            return path

    for search_path in search_paths:
        path = os.path.join(search_path, vanila_dir, subpath)
        if os.path.exists(path):
            return path
    return None

def read_template(subpath, settings=None, replacements={}):
    template_file = get_template(subpath, settings=settings)
    with open(template_file, "r") as f:
        content = f.read()
        for key in reversed(sorted(replacements.keys())):
            content = content.replace(key, replacements[key])
        return content


def get_fields_from_argv(argv, usage, argv0):
    ret = []
    for field in argv:
        try:
            field_name, field_type = field.split(':')
            if not field_type:
                usage(argv0)
        except:
            usage(argv0)
        ret.append((field_type, field_name))
    return ret


def insert_in_python(file_name, search, code_lines, in_end=False, ignore_pass=False):
    f = open(file_name, "r")
    lines = f.readlines()
    f.close()
    n = 0
    for i, line in enumerate(lines):
        if search[n] in line:
            n += 1
            if len(search) == n:
                break

    if len(search) == n:
        n = i
        n_indent = indent(lines[n])
        base_indent = None
        nn = None
        brief_started = False
        for ii, line in enumerate(lines[n + 1:]):
            i = n + 1 + ii
            if line.strip():
                if not base_indent:
                    base_indent = indent(lines[i])
                    if base_indent == n_indent:
                        nn = n
                        break
                if not brief_started:
                    if line.strip().startswith('"""'):
                        brief_started = True
                    else:
                        nn = i
                        break
                elif line.strip().startswith('"""'):
                    nn = i
                    break
        if nn != None:
            if n_indent == base_indent:
                pass
            elif not brief_started:
                if not ignore_pass and lines[nn].strip() == 'pass':
                    del lines[nn]
                    nn - 1
                if not in_end:
                    nn -= 1
            if n_indent != base_indent and in_end:
                n = nn
                for i, line in enumerate(lines[nn:]):
                    if line.strip():
                        if len(indent(line)) >= len(base_indent):
                            n = nn + i
                        else:
                            break
                nn = n

            for i, code_line in enumerate(code_lines):
                if code_line.strip():
                    lines.insert(nn + i + 1, base_indent + "{}\n".format(code_line))
                else:
                    lines.insert(nn + i + 1, "\n")

            f = open(file_name, "w")
            f.writelines(lines)
            f.close()


def patch(file_name, search, fx):
    f = open(file_name, "r")
    lines = f.readlines()
    f.close()
    n = 0
    for i, line in enumerate(lines):
        if search[n] in line:
            n += 1
            if len(search) == n:
                lines = fx(lines, i)
                break;
    f = open(file_name, "w")
    f.writelines(lines)
    f.close()


def indent(line):
    s = re.search(r'\S', line)
    if not s:
        return None
    return line[:s.span()[0]]
