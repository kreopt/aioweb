#!/usr/bin/env python3
import sys
import os
import importlib
import inflect
os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
sys.path.append( os.getcwd() )
sys.path.append( os.path.dirname(__file__) )
plague = inflect.engine()

commands={}
aliases={}
modules = []
modules_dir= os.path.join(os.path.abspath(os.path.dirname(__file__)), "modules")
briefs = {}

modules=['new']
if os.path.exists(os.path.abspath("settings.py")):
    modules_dir= os.path.join(os.path.abspath(os.path.dirname(__file__)), "modules")
    sys.path.append( modules_dir )
    for root, subdirs, files in os.walk(modules_dir):
        mods = [ f.replace(".py", "") for f in files if f.endswith(".py") and not f.startswith("__") ]
        if mods:
            r = root.replace(modules_dir, '').replace('/', '.')
            if r.startswith('.'): r = r[1:]
            if r:
                modules += [r+'.' + module for module in mods]
            else:
                modules += mods
    commands["g"] = "generate"
    commands["d"] = "destroy"
    commands["delete"] = "destroy"

for module in modules:
    try:
        m = importlib.import_module("modules." + module)
    except ImportError:
        m = importlib.import_module("wyrm.modules." + module)
    aliases = []
    try:
        aliases = m.aliases
    except AttributeError:
        pass
    briefs[module] = m.brief

    if '.' in module:
        co = commands
        mods,module_name = module.rsplit(".", 1)
        for sm in mods.split('.'):
            if co.get(sm) == None:
                co[sm] = {}
            co = co[sm]
        co[module_name] = m.execute
        for alias in aliases:
            co[alias] = module_name
    else:
        commands[module] = m.execute
        for alias in aliases:
            commands[alias] = module

def print_cmd(co, n=1, addr=[]):
    for k in co.keys():
        if type(co[k]) == dict:
            aliases = [a for a in co.keys() if co[a] == k]
            print("  "*n+ ", ".join([k]+aliases))
            print_cmd(co[k], n+1, addr+[k])
        elif type(co[k]) != str:
            aliases = [a for a in co.keys() if co[a] == k]
            ln = "  "*n+ ", ".join([k]+aliases)
            ln+=' '*(30-len(ln))
            ln+=briefs['.'.join(addr+[k])]
            print(ln)
def usage(argv0):
    print("Usage: " + argv0 + " <command> [-h|--help] [args]")
    print("")
    print("Wyrm supports these commands:")
    print_cmd(commands)
    sys.exit(1)

def execute(argv=None):
    if not argv:
        argv=sys.argv
    if len(argv) == 1:
        usage(argv[0])
    n = 1
    co = commands
    command = commands.get(argv[1])
    while not callable(command):
        if command == None:
            usage(argv[0])
        elif type(command) == str:
            command=co[command]
        else:
            co = command
            n+=1
            if n == len(argv):
                usage(argv[0])
            command= command[argv[n]]

    engine = {"commands": commands, "aliases": aliases}
    command(argv[n+1:], argv[0], engine)

if __name__ == '__main__': execute()
