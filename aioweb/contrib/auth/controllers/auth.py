import aioweb.core
from aioweb.core.controller.decorators import default_layout


@default_layout('base.html')
class AuthController(aioweb.core.Controller):

    async def index(self):
        return {}

    async def login(self):
        return {}

    async def logout(self):
        return {}

