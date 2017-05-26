#!/usr/bin/env python3
import sys
import os
import importlib
import traceback

os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
if os.environ.get("AIOWEB_SETTINGS_DIR"):
    sys.path.append(os.environ.get("AIOWEB_SETTINGS_DIR"))
sys.path.append(os.getcwd())

import wyrm.lib as lib

commands = {}
aliases = {}
modules = []
modules_dirs = [os.path.join(os.path.abspath(os.path.dirname(__file__)), "modules")]
briefs = {}

modules = []
try:
    from aioweb.conf import settings
except ImportError as e:
    # traceback.print_exc()
    settings = None

if settings: #and os.path.exists('settings.py'):
    modules_dirs.append(os.path.join(settings.BASE_DIR, "wyrm/modules"))
    sys.path.append(os.path.join(settings.BASE_DIR, "wyrm"))

    # sys.path.append( modules_dir )
    for modules_dir in modules_dirs:
        for root, subdirs, files in os.walk(modules_dir):
            mods = [f.replace(".py", "") for f in files if f.endswith(".py") and not f.startswith("__")]
            if mods:
                r = root.replace(modules_dir, '').replace('/', '.')
                if r.startswith('.'):
                    r = r[1:]
                if r:
                    modules += [r + '.' + module for module in mods]
                else:
                    modules += mods
    commands["g"] = "generate"
    commands["d"] = "destroy"
    commands["t"] = "test"
    commands["delete"] = "destroy"
    modules = list(set(modules))
else:
    modules = ['new']
    for modules_dir in modules_dirs:
        for root, subdirs, files in os.walk(os.path.join(modules_dir, "help")):
            mods = [f.replace(".py", "") for f in files if f.endswith(".py") and not f.startswith("__")]
            if mods:
                r = root.replace(modules_dir, '').replace('/', '.')
                if r.startswith('.'):
                    r = r[1:]
                if r:
                    modules += [r + '.' + module for module in mods]
                else:
                    modules += mods

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
        mods, module_name = module.rsplit(".", 1)
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

sys.path.append(os.path.dirname(__file__))


def print_cmd(co, n=1, addr=[]):
    for k in sorted(co.keys(), key=lambda k: ("zzzz" + k) if type(co[k]) == dict else k):
        if type(co[k]) == dict:
            if n == 1:
                print("")
            aliases = [a for a in co.keys() if co[a] == k]
            print("  " * n + ", ".join([k] + aliases))
            print_cmd(co[k], n + 1, addr + [k])
        elif type(co[k]) != str:
            aliases = [a for a in co.keys() if co[a] == k]
            ln = "  " * n + ", ".join([k] + aliases)
            ln += ' ' * (30 - len(ln))
            ln += briefs['.'.join(addr + [k])]
            print(ln)


def usage(argv0, co=None, addr=[]):
    print("")
    print("Usage: " + argv0 + " [OPTIONS] <command> [-h|--help] [args]")
    print("")
    print('OPTIONS:')
    print(' -e environment')
    print(' -y[es]')
    print(' -n[o]')
    print("")
    if addr:
        print('"wyrm {}" supports these subcommands:'.format(' '.join(addr)))
    else:
        print("Wyrm supports these commands:")
    print_cmd(commands if not co else co, addr=addr)
    print("")
    sys.exit(1)


def execute(argv=None):
    if not argv:
        argv = sys.argv
    while argv[1:]:
        if argv[1] not in ['-y', '-yes', '-n', '-no', '-e']:
            break
        if argv[1] == '-e':
            if len(argv) == 2:
                usage(argv[0])
            os.environ["AIOWEB_ENV"] = argv[2]
            del argv[1]
            del argv[1]
        elif argv[1] in ['-y', '-yes']:
            del argv[1]
            lib.always_say_yes()
        elif argv[1] in ['-n', '-no']:
            del argv[1]
            lib.always_say_no()

    if len(argv) == 1:
        usage(argv[0])
    n = 1
    co = commands
    command = commands.get(argv[1])
    addr = []
    while not callable(command):

        if command is None:
            usage(argv[0])
        elif type(command) == str:
            argv[n] = command
            command = co[command]
        else:
            addr.append(argv[n])
            co = command
            n += 1
            if n == len(argv):
                usage(argv[0], command, addr)
            command = command[argv[n]]

    engine = {"commands": commands, "aliases": aliases}
    command(argv[n + 1:], argv[0], engine)


if __name__ == '__main__':
    execute()
