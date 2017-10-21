class Model(object):
    db = None
    databases = None

    def __init__(self, app):
        self._app = app

    @property
    def app(self):
        return self._app

    def __call__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
