import unittest
from aiohttp.test_utils import unittest_run_loop
import wyrm.base_test
import os
import sys
from wyrm import lib
sys.path.append( os.getcwd() )


class test_NegotiationController(wyrm.base_test.AioWebTestCase):
    start_server=True
    def setUp( self ):
        super().setUp()


    @unittest_run_loop
    async def test_000_only( self ):
        rsp= await self.client.request("GET", "/test/html_only")

        self.assertEqual(rsp.status, 200)

        rsp= await self.client.request("GET", "/test/html_only", headers={
            'accept': 'application/json'
        })

        self.assertEqual(rsp.status, 406)

    @unittest_run_loop
    async def test_001_except(self):
        rsp= await self.client.request("GET", "/test/html_except")

        self.assertEqual(rsp.status, 406)

        rsp = await self.client.request("GET", "/test/html_except", headers={
            'accept': 'application/json'
        })

        self.assertEqual(rsp.status, 200)


os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
from aioweb import settings

wyrm.base_test.settings = settings
wyrm.base_test.init()
if __name__ == '__main__':
    unittest.main()

