import aioweb.core
from aioweb.core.controller.decorators import default_layout, before_action, template, layout, redirect_on_success
##from aioweb.middleware.csrf.decorators import csrf_exempt
from aiohttp import web
from app.models.crud_test import CrudTest

async def somethod(ctrl):
    print("somethod")
async def set_model(ctrl):
    ctrl.model = CrudTest.find( (await ctrl.params())["id"])
    if not ctrl.model:
        raise web.HTTPNotFound

def new_model(ctrl):
    ctrl.model = CrudTest()
    if not ctrl.model:
        raise web.HTTPNotFound

@before_action(somethod)
@before_action(new_model, only=('add', 'add_page'))
@before_action(set_model, only=('get', 'delete', 'edit_page', 'edit'))
@default_layout('base.html')
class CrudTestsController(aioweb.core.Controller):
    async def index(self):
        self.collection = CrudTest.all()
        return {"collection": self.collection, "fields": ["wtf"], "controller": self}

    async def get(self):
        return {'model': self.model, "fields": ["wtf"], "controller": self}

    # GET crud_tests/add
    async def add_page(self):
        return {'model': self.model, "controller": self}

    # @redirect_on_success('index')
    ##@csrf_exempt
    async def add(self):
        params = await self.crud_test_params()
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
        if self.model.update(**await self.crud_test_params()):
            return web.HTTPFound(self.path_for("index", None))
        return {'model': self.model, "controller": self}

    async def crud_test_params(self):
        return (await self.params())["crud_test"].permit("wtf")

