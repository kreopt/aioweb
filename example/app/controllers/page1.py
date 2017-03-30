import aioweb.core


class Page1Controller(aioweb.core.BaseController):

    def __init__(self, app):
        super().__init__(app)
        self._defaultLayout = 'base.html'

    async def index(self, request):
        return {'test': 'It works!'}

    async def csrf(self, request):
        self.use_view('page1/index.html')
        return await self.index(request)
