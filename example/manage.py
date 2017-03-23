import asyncio
import importlib
import os
import sys

os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")

import aioweb

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    app = aioweb.Application(loop=loop, middlewares=[])
    app = loop.run_until_complete(app.setup())

    if len(sys.argv) >= 1:
        try:
            mod = importlib.import_module("aioweb.management.%s" % sys.argv[1], __name__)
            run = getattr(mod, 'run')
            args = sys.argv[2:]
            run(*args)
        except (KeyError, ImportError):
            print("no such method: %s" % sys.argv[1])
