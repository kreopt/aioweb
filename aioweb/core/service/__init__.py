import importlib


class ModelInjector(object):
    def __init__(self):
        self.imported = {}

    def inject(self, name):
        imported = self.imported.get(name)
        if not imported:
            mod = importlib.import_module(f".models.{name}")
            model_class = getattr(mod, 'Model')

            imported = model_class()
            self.imported[name] = imported
        return imported

    def __getattr__(self, item):
        return self.inject(item)


class Service(object):
    def __init__(self):
        self.model = ModelInjector()