import aioweb.core


class TestController(aioweb.core.BaseController):

    async def index(self, request):
        return {'test': 'It works!'}

    async def test(self, request):
        return {'test': 'It works again!'}
