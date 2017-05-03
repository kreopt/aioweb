import unittest
import wyrm.base_test
import os, sys, shutil
from wyrm import lib
from orator.orm import Factory
sys.path.append( os.getcwd() )
from app.models.MODEL import CLASS
from tests.factories import factory
import tests.factories.TABLE_factory



class test_CLASS(wyrm.base_test.AioWebTestCase):
    def setUp( self ):
        super().setUp()

    def test_000_factory( self ):
        MODEL=factory(CLASS).create()
        self.assertTrue( MODEL.id )
        self.assertTrue( MODEL.id == CLASS.all().first().id )

if __name__ == '__main__':
    os.environ["AIOWEB_ENV"] = "test"
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    sys.path.append( os.getcwd() )
    from aioweb import settings
    wyrm.base_test.settings = settings
    lib.init_orator(settings)
    unittest.main()

