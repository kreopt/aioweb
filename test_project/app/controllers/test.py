import aioweb.core
from aioweb.core.controller.decorators import default_layout


@default_layout('base.html')
class TestController(aioweb.core.Controller):

    def __init__(self, app):
        super().__init__(app)

    async def index(self):
        return {'test': 'It works!'}

    async def test(self):
        return {'test': 'It works again!'}
