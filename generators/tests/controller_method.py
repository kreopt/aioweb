
@unittest_run_loop
async def test_METHOD( self ):
    rsp= await self.client.request("GET", "/CONTROLLER_NAME/METHOD")
    controller=self.app.last_controller
    self.assertEqual(rsp.status, 200)
