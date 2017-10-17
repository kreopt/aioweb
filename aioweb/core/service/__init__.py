import importlib

import aioweb.util


class Service(object):
    def __init__(self, app):
        self.app = app
        self.model = aioweb.util.Injector(self.app, 'Model', self.__module__)
