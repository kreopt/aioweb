import aioweb.util


class Service(object):
    def __init__(self, app):
        self._app = app
        self.model = aioweb.util.Injector(self.app, 'Model', self.__module__)
        self.service = aioweb.util.Injector(self.app, 'Service')

    @property
    def app(self):
        return self._app

    def __call__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        return self
