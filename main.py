import sys
import os

import aiohttp_debugtoolbar

os.environ.setdefault("SETTINGS_MODULE", "settings")

import asyncio
from aiohttp import web
import logging
import argparse
import settings
from core.middleware import error_pages, handle_404, handle_500
from framework.email import error_mailer
import framework


# import aiohttp_admin
# from aiohttp_admin.backends.sa import SQLiteResource

async def init(loop, argv):
    ap = argparse.ArgumentParser()
    #
    # define your command-line arguments here
    #
    options = ap.parse_args(argv)

    # setup application and extensions
    app = framework.Application(loop=loop, middlewares=[
        error_pages({404: handle_404, 500: handle_500}),
        error_mailer
        # aiohttp_debugtoolbar.middleware
    ])

    # admin_config_path = str(settings.BASE_DIR / 'static' / 'js')
    # resources = (SQLiteResource(pg, db.post, url='posts'),
    #              SQLiteResource(pg, db.tag, url='tags'),
    #              SQLiteResource(pg, db.comment, url='comments'))
    # admin = aiohttp_admin.setup(app, admin_config_path, resources=resources)

    await app.setup()

    # aiohttp_debugtoolbar.setup(app)

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
