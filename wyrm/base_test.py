import unittest
import wyrm.lib
import os

import asyncio

#from aioweb.util import awaitable
from orator.migrations import Migrator, DatabaseMigrationRepository
from orator import Model

settings = None


#def async_test(fn):
#    def decorated(self, *args, **kwargs):
#        self.loop.run_until_complete(awaitable(fn(self, *args, **kwargs)))
#    return decorated


class AioWebTestCase(unittest.TestCase):
    refresh_db_before_test = True
    start_server = False

    def __init__(self, wtf):
        super().__init__(wtf)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)
        if self.start_server:
            self.init_server()

    def __del__(self):
        self.loop.close()
        

    def refresh_db(self):
        resolver = Model.get_connection_resolver()
        repository = DatabaseMigrationRepository(resolver, 'migrations')
        migrator = Migrator(repository, resolver)
        migrator.set_connection("test")

        pretend = False

        path = wyrm.lib.dirs(settings, format=["migrations"])
        migrator.reset(path, pretend)
        migrator.run(path, pretend)

    def init_server(self):
        import aioweb
        import aiohttp.test_utils
        import config.routes as router
        self.app = aioweb.Application(loop=self.loop)
        self.loop.run_until_complete(self.app.setup())
        self.client = aiohttp.test_utils.TestClient(self.app, loop=self.loop)

    def setUp(self):
        if self.refresh_db_before_test:
            self.refresh_db()
        if self.start_server:
            self.loop.run_until_complete(self.client.start_server())
    def tearDown(self):
        if self.start_server:
            self.loop.run_until_complete(self.client.start_server())
