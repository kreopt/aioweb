import aioweb

class Service(aioweb.core.Service):

    def action(self, a, b, c):
        # using model injector
        return self.model.test.action()
