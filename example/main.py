import sys
import os

os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import asyncio
import logging
import settings
import aioweb

async def init(loop, argv):
    # setup application and extensions
    app = aioweb.Application(loop=loop)

    await app.setup()

    return app

def main(argv):
    # init logging
    logging.basicConfig(level=logging.DEBUG)

    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init(loop, argv))
    aioweb.run_app(app)

if __name__ == '__main__':
    main(sys.argv[1:])
