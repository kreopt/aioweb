import unittest
import wyrm.base_test
import os
import sys
import shutil
from wyrm import lib
sys.path.append( os.getcwd() )
from app.controllers.CONTROLLER_NAME import CLASS


class test_CLASS(wyrm.base_test.AioWebTestCase):
    def setUp( self ):
        super().setUp()
        self.request = None
        self.router  = None


if __name__ == '__main__':
    os.environ["AIOWEB_ENV"] = "test"
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    sys.path.append( os.getcwd() )
    from aioweb import settings
    wyrm.base_test.settings = settings
    lib.init_orator(settings)
    unittest.main()
