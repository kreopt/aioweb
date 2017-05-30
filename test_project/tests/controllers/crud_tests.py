import unittest
from aiohttp.test_utils import unittest_run_loop
import wyrm.base_test
import os
import sys
import shutil
from wyrm import lib
sys.path.append( os.getcwd() )
from app.controllers.crud_tests import CrudTestsController

from app.models.crud_test import CrudTest
from tests.factories import factory
import tests.factories.crud_tests_factory


class test_CrudTestsController(wyrm.base_test.AioWebTestCase):
    start_server=True
    test_field="wtf"
    test_field_value="nothing is real"
    def setUp( self ):
        super().setUp()
        self.collection=[]
        for i in range(1,4):
            self.collection.append(factory(CrudTest).create())

    async def receive_csrf( self ): 
        rsp= await self.client.request("GET", "/crud_tests")
        return rsp.headers['X-Csrf-Token']

    def post_data( self ):
        ret = {}
        ret['crud_test[{}]'.format(self.test_field)]= self.test_field_value
        return ret


    async def post_data_with_csrf( self ):
        csrf = await self.receive_csrf()
        ret = self.post_data()
        ret["csrftoken"] = csrf
        return ret

    # GET /crud_tests
    @unittest_run_loop
    async def test_000_index( self ):
        rsp= await self.client.request("GET", "/crud_tests")
        controller=self.app.last_controller
        self.assertEqual(rsp.status, 200)
        c_ids= list(map(lambda m: m.id, controller.collection))
        ids= list(map(lambda m: m.id, CrudTest.all()))
        self.assertEqual(ids, c_ids)
        self.assertEqual(len(c_ids), len(self.collection))

    # GET /crud_tests/:id
    @unittest_run_loop
    async def test_001_get( self ):
        rsp= await self.client.request("GET", "/crud_tests/{}".format(self.collection[0].id))
        controller=self.app.last_controller
        self.assertEqual(rsp.status, 200)
        self.assertEqual(controller.model.id, self.collection[0].id)

    # GET /crud_tests/:invalid_id
    @unittest_run_loop
    async def test_001_get_should_return_404( self ):
        rsp= await self.client.request("GET", "/crud_tests/{}".format(666))
        controller=self.app.last_controller
        self.assertEqual(rsp.status, 404)

    # GET /crud_tests/:id/edit
    @unittest_run_loop
    async def test_002_edit_page( self ):
        rsp= await self.client.request("GET", "/crud_tests/{}/edit".format(self.collection[0].id))
        controller=self.app.last_controller
        self.assertEqual(rsp.status, 200)
        self.assertEqual(controller.model.id, self.collection[0].id)

    # GET /crud_tests/:invalid_id/edit
    @unittest_run_loop
    async def test_002_edit_page_should_return_404( self ):
        rsp= await self.client.request("GET", "/crud_tests/{}/edit".format(666))
        controller=self.app.last_controller
        self.assertEqual(rsp.status, 404)

    # POST /crud_tests/:id
    @unittest_run_loop
    async def test_003_edit( self ):
        post_data = await self.post_data_with_csrf()
        model_id = self.collection[0].id
        rsp= await self.client.post("/crud_tests/{}".format(model_id), data=post_data)
        controller=self.app.last_controller
        self.assertEqual(rsp.status, 200)
        model=CrudTest.find(model_id)
        self.assertEqual(getattr(model, self.test_field), self.test_field_value)


    # POST /crud_tests/:id (CSRF error)
    @unittest_run_loop
    async def test_003_edit_without_csrf( self ):
        post_data = self.post_data()
        model_id = self.collection[0].id
        rsp= await self.client.post("/crud_tests/{}".format(model_id), data=post_data)
        controller=self.app.last_controller
        self.assertEqual(rsp.status, 403)

    # GET /crud_tests/add 
    @unittest_run_loop
    async def test_004_add_page( self ):
        rsp= await self.client.request("GET", "/crud_tests/add")
        controller=self.app.last_controller
        self.assertEqual(rsp.status, 200)


    # POST /crud_tests/add 
    @unittest_run_loop
    async def test_005_add( self ):
        total_count = CrudTest.count()
        post_data = await self.post_data_with_csrf()
        total_count+= 1
        rsp= await self.client.post("/crud_tests/add", data=post_data)
        self.assertEqual(rsp.status, 200)
        self.assertEqual(total_count, CrudTest.count())

    # POST /crud_tests/add 
    @unittest_run_loop
    async def test_005_add_without_csrf( self ):
        post_data = self.post_data()
        rsp= await self.client.post("/crud_tests/add", data=post_data)
        self.assertEqual(rsp.status, 403)

    # DELETE /crud_tests/:id/delete
    @unittest_run_loop
    async def test_006_delete( self ):
        csrf = await self.receive_csrf()
        model_id = self.collection[0].id
        total_count = CrudTest.count()
        rsp= await self.client.post("/crud_tests/{}/delete".format(model_id), data={"csrftoken": csrf})
        total_count-= 1
        self.assertEqual(rsp.status, 200)
        self.assertEqual(total_count, CrudTest.count())
    # DELETE /crud_tests/:id/delete (CSRF error)
    @unittest_run_loop
    async def test_006_delete_with_wrong_csrf( self ):
        csrf = await self.receive_csrf() + "dsadas"
        model_id = self.collection[0].id
        rsp= await self.client.post("/crud_tests/{}/delete".format(model_id), data={"csrftoken": csrf})
        self.assertEqual(rsp.status, 403)


if __name__ == '__main__':
    os.environ["AIOWEB_ENV"] = "test"
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    sys.path.append( os.getcwd() )
    from aioweb import settings
    wyrm.base_test.settings = settings
    lib.init_orator(settings)
    unittest.main()

