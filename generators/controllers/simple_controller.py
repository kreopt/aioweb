import aioweb.core


class CLASS(aioweb.core.BaseController):
    def __init__(self, app):
        super().__init__(app)
        self._defaultLayout = 'base.html'
