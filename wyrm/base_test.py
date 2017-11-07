import unittest
import asyncio

from aioweb.modules.db import init_db

import aioweb
import aiohttp.test_utils


def init():
    pass


class AioWebTestCase(unittest.TestCase):
    refresh_db_before_test = True
    start_server = False

    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)
        self._priv={}

        # self.loop.run_until_complete(init_db(self))

        if self.start_server:
            self.init_server()

        self.addCleanup(self.cleanup)

    def cleanup(self):
        if self.app:
            self.loop.run_until_complete(self.app.shutdown())
            self.loop.run_until_complete(self.app.cleanup())
        self.loop.close()

    def __setitem__(self, key, value):
        self._priv[key] = value

    def __getitem__(self, item):
        return self._priv.get(item)

    def refresh_db(self):
        pass

    def init_server(self):
        self.app = aioweb.Application(loop=self.loop)
        self.loop.run_until_complete(self.app.setup())
        self.client = aiohttp.test_utils.TestClient(aiohttp.test_utils.TestServer(self.app), loop=self.loop)

    def setUp(self):
        if self.refresh_db_before_test:
            self.refresh_db()
        if self.start_server:
            self.loop.run_until_complete(self.client.start_server())

    def tearDown(self):
        if self.start_server:
            self.loop.run_until_complete(self.client.close())
