import sys
import os

os.environ.setdefault("SETTINGS_MODULE", "settings")

import asyncio
import logging
import settings
from aioweb.email import error_mailer
import aioweb

async def init(loop, argv):
    # setup application and extensions
    app = aioweb.Application(loop=loop, middlewares=[
        error_mailer
    ])

    await app.setup()

    return app


def main(argv):
    # init logging
    logging.basicConfig(level=logging.DEBUG)

    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init(loop, argv))
    aioweb.run_app(app)


def get_app(loop):
    return init(loop, [])

if __name__ == '__main__':
    main(sys.argv[1:])
