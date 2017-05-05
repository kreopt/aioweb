
@unittest_run_loop
async def test_METHOD( self ):
    #CONTROLLER_NAME_controller = CLASS(self.request, self.router)
    rsp= await self.client.request("GET", "/")
    print(rsp.status)
    self.assertTrue(rsp.status == 200)
