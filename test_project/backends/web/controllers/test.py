import aioweb.core
from aioweb.core.controller.decorators import default_layout, content_type


@default_layout('base.html')
class TestController(aioweb.core.Controller):

    async def index(self):
        # using service injector
        return {'test': self.service.test1.action()}