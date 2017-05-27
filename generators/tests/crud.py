import unittest
from aiohttp.test_utils import unittest_run_loop
import wyrm.base_test
import os
import sys
import shutil
from wyrm import lib
sys.path.append( os.getcwd() )
from app.controllers.TABLE import CONTROLLER_CLASS

from app.models.MODEL import MODEL_CLASS
from tests.factories import factory
import tests.factories.TABLE_factory


class test_CONTROLLER_CLASS(wyrm.base_test.AioWebTestCase):
    start_server=True
    test_field="TEST_FIELD"
    test_field_value="nothing is real"
    def setUp( self ):
        super().setUp()
        self.collection=[]
        for i in range(1,4):
            self.collection.append(factory(MODEL_CLASS).create())

    async def receive_csrf( self ): 
        rsp= await self.client.request("GET", "/TABLE")
        return rsp.headers['X-Csrf-Token']

    def post_data( self ):
        ret = {}
        ret['MODEL[{}]'.format(self.test_field)]= self.test_field_value
        return ret


    async def post_data_with_csrf( self ):
        csrf = await self.receive_csrf()
        ret = self.post_data()
        ret["csrftoken"] = csrf
        return ret

    # GET /TABLE
    @unittest_run_loop
    async def test_000_index( self ):
        rsp= await self.client.request("GET", "/TABLE")
        controller=self.app.last_controller
        self.assertEqual(rsp.status, 200)
        c_ids= list(map(lambda m: m.id, controller.collection))
        ids= list(map(lambda m: m.id, MODEL_CLASS.all()))
        self.assertEqual(ids, c_ids)
        self.assertEqual(len(c_ids), len(self.collection))

    # GET /TABLE/:id
    @unittest_run_loop
    async def test_001_get( self ):
        rsp= await self.client.request("GET", "/TABLE/{}".format(self.collection[0].id))
        controller=self.app.last_controller
        self.assertEqual(rsp.status, 200)
        self.assertEqual(controller.model.id, self.collection[0].id)

    # GET /TABLE/:invalid_id
    @unittest_run_loop
    async def test_001_get_should_return_404( self ):
        rsp= await self.client.request("GET", "/TABLE/{}".format(666))
        controller=self.app.last_controller
        self.assertEqual(rsp.status, 404)

    # GET /TABLE/:id/edit
    @unittest_run_loop
    async def test_002_edit_page( self ):
        rsp= await self.client.request("GET", "/TABLE/{}/edit".format(self.collection[0].id))
        controller=self.app.last_controller
        self.assertEqual(rsp.status, 200)
        self.assertEqual(controller.model.id, self.collection[0].id)

    # GET /TABLE/:invalid_id/edit
    @unittest_run_loop
    async def test_002_edit_page_should_return_404( self ):
        rsp= await self.client.request("GET", "/TABLE/{}/edit".format(666))
        controller=self.app.last_controller
        self.assertEqual(rsp.status, 404)

    # POST /TABLE/:id
    @unittest_run_loop
    async def test_003_edit( self ):
        post_data = await self.post_data_with_csrf()
        model_id = self.collection[0].id
        rsp= await self.client.post("/TABLE/{}".format(model_id), data=post_data)
        controller=self.app.last_controller
        self.assertEqual(rsp.status, 200)
        model=MODEL_CLASS.find(model_id)
        self.assertEqual(getattr(model, self.test_field), self.test_field_value)


    # POST /TABLE/:id (CSRF error)
    @unittest_run_loop
    async def test_003_edit_without_csrf( self ):
        post_data = self.post_data()
        model_id = self.collection[0].id
        rsp= await self.client.post("/TABLE/{}".format(model_id), data=post_data)
        controller=self.app.last_controller
        self.assertEqual(rsp.status, 403)

    # GET /TABLE/add 
    @unittest_run_loop
    async def test_004_add_page( self ):
        rsp= await self.client.request("GET", "/TABLE/add")
        controller=self.app.last_controller
        self.assertEqual(rsp.status, 200)


    # POST /TABLE/add 
    @unittest_run_loop
    async def test_005_add( self ):
        total_count = MODEL_CLASS.count()
        post_data = await self.post_data_with_csrf()
        total_count+= 1
        rsp= await self.client.post("/TABLE/add", data=post_data)
        self.assertEqual(rsp.status, 200)
        self.assertEqual(total_count, MODEL_CLASS.count())

    # POST /TABLE/add 
    @unittest_run_loop
    async def test_005_add_without_csrf( self ):
        post_data = self.post_data()
        rsp= await self.client.post("/TABLE/add", data=post_data)
        self.assertEqual(rsp.status, 403)

    # DELETE /TABLE/:id/delete
    @unittest_run_loop
    async def test_006_delete( self ):
        csrf = await self.receive_csrf()
        model_id = self.collection[0].id
        total_count = MODEL_CLASS.count()
        rsp= await self.client.post("/TABLE/{}/delete".format(model_id), data={"csrftoken": csrf})
        total_count-= 1
        self.assertEqual(rsp.status, 200)
        self.assertEqual(total_count, MODEL_CLASS.count())
    # DELETE /TABLE/:id/delete (CSRF error)
    @unittest_run_loop
    async def test_006_delete_with_wrong_csrf( self ):
        csrf = await self.receive_csrf() + "dsadas"
        model_id = self.collection[0].id
        rsp= await self.client.post("/TABLE/{}/delete".format(model_id), data={"csrftoken": csrf})
        self.assertEqual(rsp.status, 403)


if __name__ == '__main__':
    os.environ["AIOWEB_ENV"] = "test"
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    sys.path.append( os.getcwd() )
    from aioweb import settings
    wyrm.base_test.settings = settings
    lib.init_orator(settings)
    unittest.main()

