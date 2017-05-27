import aioweb.core
from aioweb.core.controller.decorators import default_layout, before_action, template, layout, redirect_on_success
##from aioweb.middleware.csrf.decorators import csrf_exempt
from aiohttp import web
from app.models.MODEL import MODEL_CLASS

async def set_model(ctrl):
    ctrl.model = MODEL_CLASS.find( (await ctrl.params())["id"])
    if not ctrl.model:
        raise web.HTTPNotFound

def new_model(ctrl):
    ctrl.model = MODEL_CLASS()
    if not ctrl.model:
        raise web.HTTPNotFound

@before_action(new_model, only=('add', 'add_page'))
@before_action(set_model, only=('get', 'delete', 'edit_page', 'edit'))
@default_layout('base.html')
class CONTROLLER_CLASS(aioweb.core.Controller):
    async def index(self):
        self.collection = MODEL_CLASS.all()
        return {"collection": self.collection, "fields": [MODEL_FIELD_NAMES], "controller": self}

    async def get(self):
        return {'model': self.model, "fields": [MODEL_FIELD_NAMES], "controller": self}

    # GET TABLE/add
    async def add_page(self):
        return {'model': self.model, "controller": self}

    # @redirect_on_success('index')
    ##@csrf_exempt
    async def add(self):
        params = await self.MODEL_params()
        for k,v in params.items():
            setattr(self.model, k, v)
        if self.model.save():
            return web.HTTPFound(self.path_for("index", None))
        return {'model': self.model, "controller": self}

    # @redirect_on_success('index')
    async def delete(self):
        if self.model.delete():
            return web.HTTPFound(self.path_for("index", None))

    async def edit_page(self):
        return {'model': self.model, "controller": self}

    #@redirect_on_success('index')
    ##@csrf_exempt
    async def edit(self):
        if self.model.update(**await self.MODEL_params()):
            return web.HTTPFound(self.path_for("index", None))
        return {'model': self.model, "controller": self}

    async def MODEL_params(self):
        return (await self.params())["MODEL"].permit(MODEL_FIELD_NAMES)

