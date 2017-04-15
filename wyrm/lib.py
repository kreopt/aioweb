import os, sys, re, importlib
import inflection
vanila_dir="/usr/share/aioweb/generators"
# def asc
# def names
# def dirs
# def get_import
# def get_template
# def insert_in_python
# def indent

def init_orator(settings):
    import yaml
    from orator import DatabaseManager
    from orator import Model
    with open(os.path.join( settings.BASE_DIR, "config/database.yml"), "r") as f:
        dbconfig=yaml.load( f.read() )
        dbconfig = dbconfig["databases"]
        environment = os.getenv("AIOWEB_ENV", dbconfig["default"])
        dbconfig["default"] = environment
        if dbconfig[environment]["driver"] == "sqlite":
            dbconfig[environment]["database"]=os.path.join( settings.BASE_DIR, "db/{}".format(dbconfig[environment]["database"]) )

    Model.set_connection_resolver( DatabaseManager(dbconfig) )

def ask(question, answers=["y", "n"]):
    while True:
        print(question + " [" + ",".join(answers) + "]" )
        rc = sys.stdin.readline().strip().lower()
        if rc in answers: return rc
        else:
            print("You bastard gimme a correct answer")

def names(word, format=[]):
    ret = {}
    ret["table"] = inflection.tableize(word)
    ret["model"] = inflection.singularize( ret["table"] )
    ret["class"] = inflection.camelize( ret["model"] )
    if not format: return ret
    ret= [ret[k] for k in format]
    return ret[0] if len(ret)==1 else ret

def dirs(settings, app=None, format=[], check=False):
    base_dir = os.path.dirname(importlib.util.find_spec(app).origin) if app  else settings.BASE_DIR
    ret={}
    ret["config"]      = os.path.join(base_dir, "config")
    ret["tests"]       = os.path.join(base_dir, "tests")
    ret["factories"]   = os.path.join(base_dir, "tests/factories")
    ret["models"]      = os.path.join(base_dir, "models" if app else "app/models")
    ret["controllers"] = os.path.join(base_dir, "controllers" if app else "app/controllers")
    ret["views"]       = os.path.join(base_dir, "views" if app else "app/views")
    ret["migrations"]  = os.path.join(base_dir, "migrations" if app else "db/migrations")
    if check:
        for k in ret.keys():
            if not os.path.exists(ret[k]): ret[k]=None
    if not format: return ret
    ret= [ret[k] for k in format]
    return ret[0] if len(ret)==1 else ret

def get_import(category, component, app=None):
    return ( app if app else "app" ) + ".{}.{}".format(category, component)


def get_template(subpath):
    path=os.path.abspath(subpath)
    if os.path.exists( path ): return path 
    path=os.path.join(vanila_dir, subpath)
    if os.path.exists( path ): return path 
    return None

def get_fields_from_argv(argv, usage, argv0):
    ret=[]
    for field in argv:
        try:
            field_name, field_type = field.split(':')
            if not field_type:
                usage(argv0)
        except:
            usage(argv0)
        ret.append( (field_type, field_name) )
    return ret

def insert_in_python(file_name, search, code_lines, in_end=False, ignore_pass=False):
    f= open(file_name, "r")
    lines=f.readlines() 
    f.close()
    n = 0
    for i,line in enumerate(lines):
        if search[n] in line:
            n+=1
            if len(search) == n: 
                break

    if len(search) == n:
        n=i
        n_indent = indent(lines[n])
        base_indent = None
        nn = None
        brief_started = False
        for ii,line in enumerate(lines[n+1:]):
            i = n+1 + ii
            if line.strip():
                if not base_indent:
                    base_indent = indent(lines[i])
                    if base_indent == n_indent:
                        nn=n
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
                    nn-1
                if not in_end: nn-=1
            if n_indent != base_indent and in_end:
                n = nn
                for i, line in enumerate(lines[nn:]):
                    if line.strip():
                        if len( indent(line) ) >= len( base_indent ):
                            n = nn+i
                        else: break
                nn = n
                        
            for i, code_line in enumerate(code_lines):
                if code_line.strip():
                    lines.insert(nn+i+1, base_indent+"{}\n".format(code_line))
                else:
                    lines.insert(nn+i+1, "\n")

            f=open(file_name, "w")
            f.writelines(lines)
            f.close()

def patch(file_name, search, fx):
    f= open(file_name, "r")
    lines=f.readlines() 
    f.close()
    n = 0
    for i,line in enumerate(lines):
        if search[n] in line:
            n+=1
            if len(search) == n:
                lines = fx(lines, i)
                break;
    f=open(file_name, "w")
    f.writelines(lines)
    f.close()

def indent(line):
    s=re.search(r'\S', line)
    if not s: return None
    return line[:s.span()[0]]
