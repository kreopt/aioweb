import filecmp
import getpass
import sys
import os

brief = "collect static files"


import importlib.util
import os
import shutil

from optparse import OptionParser


def recursive_overwrite(src, dest, ignore=None):
    if os.path.isdir(src):
        if not os.path.isdir(dest):
            os.makedirs(dest, exist_ok=True)
        files = os.listdir(src)
        if ignore is not None:
            ignored = ignore(src, files)
        else:
            ignored = set()
        for f in files:
            if f not in ignored:
                recursive_overwrite(os.path.join(src, f),
                                    os.path.join(dest, f),
                                    ignore)
    else:
        if not os.path.exists(dest) or not filecmp.cmp(src, dest):
            print('copy {}'.format(src))
            shutil.copyfile(src, dest)
            shutil.copystat(src, dest)

def collectstatic(src_dir, dst_dir, ignore=None, overwrite=True):
    os.makedirs(dst_dir, exist_ok=True)

    if os.path.exists(src_dir):
        recursive_overwrite(src_dir, dst_dir, ignore=ignore)


def execute(argv, argv0, engine):
    import lib, importlib, re
    import code
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    from aioweb import settings
    sys.path.append(settings.BASE_DIR)
    # Initialize Orator ORM

    parser = OptionParser()
    parser.add_option("--no-input", help="ask confirmation before collecting", action="store_true", dest="silent")
    (options, args) = parser.parse_args()
    if options.silent:
        agree = 'y'
    else:
        agree = input("Do you want to overwrite your assets dir? [y/n] ")
    if agree.lower() == 'y':
        DEST_DIR = os.path.join(settings.BASE_DIR, 'public')
        if os.path.exists(DEST_DIR):
            shutil.rmtree(DEST_DIR)
        else:
            os.makedirs(DEST_DIR)

        path = os.path.join(settings.BASE_DIR, 'app', 'assets')
        if os.path.exists(path):
            recursive_overwrite(path, DEST_DIR)
        for appName in settings.APPS:
            try:
                path = os.path.join(os.path.dirname(importlib.util.find_spec(appName).origin), 'assets')
                if os.path.exists(path):
                    print("collecting %s" % path)
                    recursive_overwrite(path, DEST_DIR)
            except ImportError as exc:
                # traceback.print_exc()
                print("no such module: %s" % appName)
