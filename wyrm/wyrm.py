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
modules=['new']
if os.path.exists(os.path.abspath("settings.py")):
    modules_dir= os.path.join(os.path.abspath(os.path.dirname(__file__)), "modules")
    sys.path.append( modules_dir )
    modules = [module.replace(".py", "") for module in os.listdir(modules_dir) if os.path.isfile( os.path.join(modules_dir, module) ) and module.endswith(".py") and module!='__init__.py']

for module in modules:
    try:
        m = importlib.import_module("modules." + module)
    except ImportError:
        m = importlib.import_module("wyrm.modules." + module)
    commands[module] = m.execute
    for alias in m.aliases:
        try:
            aliases[alias] = module
        except:
            pass

def usage(argv0):
    print("Usage: " + argv0 + " <command> [-h|--help] [args]")
    print("")
    print("Wyrm supports these commands:")
    for c in commands.keys():
        print("  " + c)
    sys.exit(1)

def execute(argv=None):
    if not argv:
        argv=sys.argv
    if len(argv) == 1:
        usage(argv[0])
    argv1=argv[1]
    command= commands.get(argv1)
    if not command:  command = commands.get(aliases.get(argv1))
    if command:
        engine = {"commands": commands, "aliases": aliases}
        command(argv[2:], argv[0], engine)
    else:
        usage(argv[0])

if __name__ == '__main__': execute()
