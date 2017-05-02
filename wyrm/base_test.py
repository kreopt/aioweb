import unittest
import wyrm.lib
import os

import asyncio

from aioweb.util import awaitable
from orator.migrations import Migrator, DatabaseMigrationRepository
from orator import Model

settings = None


def async_test(fn):
    def decorated(self, *args, **kwargs):
        self._loop.run_until_complete(awaitable(fn(self, *args, **kwargs)))
    return decorated


class AioWebTestCase(unittest.TestCase):
    refresh_db_before_test = True

    def __init__(self, wtf):
        super().__init__(wtf)
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

    def refresh_db(self):
        resolver = Model.get_connection_resolver()
        repository = DatabaseMigrationRepository(resolver, 'migrations')
        migrator = Migrator(repository, resolver)
        migrator.set_connection("test")

        pretend = False

        path = wyrm.lib.dirs(settings, format=["migrations"])
        migrator.reset(path, pretend)
        migrator.run(path, pretend)

    def setUp(self):
        if self.refresh_db_before_test:
            self.refresh_db()
