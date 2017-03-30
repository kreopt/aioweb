import asyncio

import logging

import aioweb


async def init(loop, argv):
    # setup application and extensions
    app = aioweb.Application(loop=loop)
    await app.setup()
    return app


def run(app, *args, **kwargs):
    logging.basicConfig(level=logging.DEBUG)

    aioweb.run_app(app)
