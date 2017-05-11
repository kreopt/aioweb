import aioweb.core
from aioweb.core.controller.decorators import default_layout


@default_layout('base.html')
class TestController(aioweb.core.Controller):

    async def index(self):
        return {'test': 'It works!'}

    async def test(self):
        return {'test': 'It works again!'}
