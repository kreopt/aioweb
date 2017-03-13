import sys
import os

os.environ.setdefault("SETTINGS_MODULE", "settings")

import asyncio
import logging
import settings
from framework.email import error_mailer
import framework

async def init(loop, argv):
    # setup application and extensions
    app = framework.Application(loop=loop, middlewares=[
        error_mailer
    ])

    await app.setup()

    return app


def main(argv):
    # init logging
    logging.basicConfig(level=logging.DEBUG)

    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init(loop, argv))
    framework.run_app(app)


def get_app(loop):
    return init(loop, [])

if __name__ == '__main__':
    main(sys.argv[1:])
