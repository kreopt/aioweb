import aioweb.core


class AdminController(aioweb.core.Controller):
    def __init__(self, app):
        super().__init__(app)
        self._defaultLayout = 'base.html'

    async def index(self, request):
        return {}
