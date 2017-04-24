import sys
import os

brief = "start the aioweb server"
aliases = ["s", "runserver"]


def execute(argv, argv0, engine):
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    sys.path.append(os.getcwd())

    import asyncio
    import logging
    import settings
    import aioweb
    async def init(loop, argv):
        # setup application and extensions
        app = aioweb.Application(loop=loop)

        await app.setup()

        return app

    # init logging
    logging.basicConfig(level=logging.DEBUG)

    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init(loop, argv))
    aioweb.run_app(app)
