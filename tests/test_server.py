import pytest

import aioweb

class Test:
    def __init__(self, event_loop):

        self.app = event_loop.run_until_complete(self.init(event_loop, []))
        aioweb.run_app(self.app)

    async def init(loop, argv):
        # setup application and extensions
        app = aioweb.Application(loop=loop, middlewares=[])

        await app.setup()

        return app