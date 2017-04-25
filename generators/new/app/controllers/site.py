import aioweb.core
from aioweb.core.controller.decorators import default_layout


@default_layout('base.html')
class SiteController(aioweb.core.Controller):

    async def index(self):
        return {'test': 'It works!'}

