from aiohttp import web

from .site import MODELS

async def list(request, model):
    try:
        items = MODELS[model]

    except KeyError:
        return web.HTTPNotFound()

async def edit_page(request, model, pk):
    pass

async def add_page(request, model):
    pass


class ModelAdmin(object):
    def __init__(self):
        pass

    async def get(self, request):
        pass

    async def post(self, request):
        pass

    async def patch(self, request):
        pass

    async def delete(self, request):
        pass