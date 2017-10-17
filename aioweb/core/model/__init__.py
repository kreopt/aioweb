class Model(object):
    db = None
    databases = None

    def __init__(self, app):
        self.app = app
