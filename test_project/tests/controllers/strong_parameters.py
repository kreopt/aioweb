import unittest
from aiohttp.test_utils import unittest_run_loop
import wyrm.base_test
import os
import sys
import shutil
from wyrm import lib
sys.path.append( os.getcwd() )
from app.controllers.strong_parameters import StrongParametersController
from aioweb.core.controller.strong_parameters import StrongParameters


class test_StrongParametersController(wyrm.base_test.AioWebTestCase):
    start_server=True
    refresh_db_before_test = False
    def setUp( self ):
        super().setUp()

    @unittest_run_loop
    async def test_strong_parameters( self ):
        rsp= await self.client.request("GET", "/strong_parameters/test?a=1&b=2&c=3&d[a]=1&d[b]=2&d[c]=3&e[][f]=6&e[][g]=7")
        self.assertEqual(rsp.status, 200)
        controller=self.app.last_controller

        params = await controller.params()
        self.assertIsInstance(params, StrongParameters)
        self.assertEqual(params, {  'a': '1', 'b': '2', 'c': '3', 'd': {'a': '1', 'b': '2', 'c': '3'}, 'e': [{'f': '6'}, {'g': '7'}]} )
        self.assertEqual(params.permit('a', 'b'), {'a': '1', 'b': '2'})
        self.assertEqual(params.permit('a', 'b', 'd'), {'a': '1', 'b': '2'})
        self.assertEqual(params.permit(str), {'a': '1', 'b': '2', 'c': '3'})
        self.assertEqual(params.permit({'d': ['a', 'c']}), {'d': {'a': '1', 'c': '3'}})

    @unittest_run_loop
    async def test_strong_parameters2( self ):
        rsp= await self.client.request("GET", "/strong_parameters/test?a[1][a]=1&a[1][b]=2&a[1][c]=3&a[2][a]=4&a[2][b]=5")
        self.assertEqual(rsp.status, 200)
        controller=self.app.last_controller

        params = await controller.params()
        self.assertIsInstance(params, StrongParameters)
        self.assertEqual(params, {  'a': {'1': {'a': '1', 'b': '2', 'c': '3'}, '2': {'a': '4', 'b': '5'}} })
        self.assertEqual(params.permit({'a': {str: ['a', 'c']}}), {  'a': {'1': {'a': '1', 'c': '3'}, '2': {'a': '4'}} })
        self.assertEqual(params.permit({'a': {list: ['a', 'c']}}), {  'a': [{'a': '1', 'c': '3'}, {'a': '4'}] })





if __name__ == '__main__':
    os.environ["AIOWEB_ENV"] = "test"
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    sys.path.append( os.getcwd() )
    from aioweb import settings
    wyrm.base_test.settings = settings
    lib.init_orator(settings)
    unittest.main()
