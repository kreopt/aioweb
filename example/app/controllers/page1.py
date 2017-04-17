import aioweb.core


class Page1Controller(aioweb.core.BaseController):

    def __init__(self, request):
        super().__init__(request)
        self._defaultLayout = 'base.html'

    async def index(self):
        return {'test': 'It works!'}

    async def csrf(self):
        self.use_view('page1/index.html')
        return await self.index()
