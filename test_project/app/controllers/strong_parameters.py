import aioweb.core
from aioweb.core.controller.decorators import default_layout


@default_layout('base.html')
class StrongParametersController(aioweb.core.Controller):
    pass

    async def test(self):
        return {}

