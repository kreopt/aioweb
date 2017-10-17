import aioweb

class Service(aioweb.core.Service):

    def action(self, a, b, c):
        # using model injector
        self.model.test.action()