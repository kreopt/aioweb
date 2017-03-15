import aioweb.core


class TestController(aioweb.core.BaseController):

    def __init__(self, app):
        super().__init__(app)
        self._defaultLayout = 'base.html'

    async def index(self, request):
        return {'test': 'It works!'}

    async def test(self, request):
        return {'test': 'It works again!'}
