import aioweb.core
from aioweb.core.controller.decorators import default_layout, content_type


@default_layout('base.html')
class TestController(aioweb.core.Controller):

    async def index(self):
        return {'test': 'It works!'}

    async def test(self):
        return {'test': 'It works again!'}

    @content_type(only=['text/html'])
    async def html_only(self):
        return {}

    @content_type(exclude=['text/html'])
    async def html_except(self):
        return {}
