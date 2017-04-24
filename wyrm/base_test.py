import unittest, wyrm.lib, os
from orator.migrations import Migrator, DatabaseMigrationRepository
from orator import Model

settings = None


class AoiWebTestCase(unittest.TestCase):
    refresh_db_before_test = True

    def __init__(self, wtf):
        super().__init__(wtf)

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
