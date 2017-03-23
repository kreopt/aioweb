import asyncio

import logging

import aioweb


async def init(loop, argv):
    # setup application and extensions
    app = aioweb.Application(loop=loop)

    await app.setup()

    return app


def run(*args, **kwargs):
    logging.basicConfig(level=logging.DEBUG)

    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init(loop, *args, **kwargs))
    aioweb.run_app(app)
