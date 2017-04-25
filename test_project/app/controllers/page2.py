import aioweb.core


class Page2Controller(aioweb.core.Controller):

    def __init__(self, request):
        super().__init__(request)
        self._defaultLayout = 'base.html'

    async def index(self):
        return {'test': 'It works!'}
