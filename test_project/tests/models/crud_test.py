import unittest
import wyrm.base_test
import os, sys, shutil
from wyrm import lib
from orator.orm import Factory
sys.path.append( os.getcwd() )
from app.models.crud_test import CrudTest
from tests.factories import factory
import tests.factories.crud_tests_factory



class test_CrudTest(wyrm.base_test.AioWebTestCase):
    def setUp( self ):
        super().setUp()

    def test_000_factory( self ):
        crud_test=factory(CrudTest).create()
        self.assertTrue( crud_test.id )
        self.assertTrue( crud_test.id == CrudTest.all().first().id )

if __name__ == '__main__':
    os.environ["AIOWEB_ENV"] = "test"
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    sys.path.append( os.getcwd() )
    from aioweb import settings
    wyrm.base_test.settings = settings
    lib.init_orator(settings)
    unittest.main()

