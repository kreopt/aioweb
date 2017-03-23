from aiohttp import web
from aiohttp_jinja2 import render_template
from orator.exceptions.query import QueryException

from aioweb.admin import form
from aioweb.admin.form import FieldInstance
from aioweb.auth import login_required
from aioweb.render import template
import inspect

from .site import MODELS


class ModelAdmin(object):
    def __init__(self, model=''):
        self.model = model
        pass

    @login_required()
    async def add(self, request):
        post = await request.post()
        inlines = getattr(MODELS[request.match_info['model']].Admin, '__inline__', [])

        model = MODELS[request.match_info['model']]

        item = model()

        for inline in inlines:
            iitem = inline[0]()
            for field in post:
                f = field.split('.')
                if f[0] == inline[0].__name__:
                    setattr(iitem, f[1], post[field])

            try:
                iitem.save()
            except QueryException:
                return render_template('admin/add.html', request, {
                    'error': 'db_error'
                })
            setattr(item, inline[1], getattr(iitem, inline[2]))

        for field in post:
            f = field.split('.')
            if f[0] == model.__name__:
                setattr(item, f[1], post[field])
        try:
            item.save()
            if request.is_ajax():
                return web.HTTPOk()
            else:
                return web.HTTPFound('/admin/%s/' % request.match_info['model'])
        except QueryException:
            return render_template('admin/add.html', request, {
                'error': 'db_error'
            })

    @login_required()
    async def edit(self, request):
        item = MODELS[request.match_info['model']].find_or_fail(request.match_info['id'])
        post = await request.post()
        inlines = getattr(MODELS[request.match_info['model']].Admin, '__inline__', [])

        for inline in inlines:
            iitem = inline[0].find_or_fail(getattr(item, inline[1]))
            for field in post:
                f = field.split('.')
                if f[0] == inline[0].__name__ and hasattr(iitem, f[1]):
                    setattr(iitem, f[1], post[field])
            iitem.save()


        for field in post:
            f = field.split('.')
            if f[0] == MODELS[request.match_info['model']].__name__ and hasattr(item, f[1]):
                setattr(item, f[1], post[field])
        try:
            item.save()

            if request.is_ajax():
                return web.HTTPOk()
            else:
                return web.HTTPFound('/admin/%s/' % request.match_info['model'])
        except QueryException:
            return render_template('admin/edit.html', request, {
                'error': 'db_error'
            })

    @login_required()
    async def delete(self, request):
        MODELS[request.match_info['model']].delete(request.match_info['id'])
        if request.is_ajax():
            return web.HTTPOk()
        else:
            return web.HTTPFound('/admin/list/')


    @template('admin/list.html')
    @login_required()
    async def list(self, request):
        try:
            items = MODELS[request.match_info['model']].all()
        except KeyError:
            return web.HTTPNotFound()
        except Exception as e:
            return web.HTTPNotFound()
        return {
            'model': request.match_info['model'],
            'items': items
        }

    def get_model_fields(self, model):
        if hasattr(model, 'Admin'):
            return inspect.getmembers(model.Admin, lambda e: isinstance(e, form.FormField))
        return []

    @template('admin/edit.html')
    @login_required()
    async def edit_page(self, request):
        item = MODELS[request.match_info['model']].find_or_fail(request.match_info['id'])
        fields = self.get_model_fields(MODELS[request.match_info['model']])
        inlines = getattr(MODELS[request.match_info['model']].Admin, '__inline__', [])
        field_instances = []

        for inline in inlines:
            iitem = inline[0].find_or_fail(getattr(item, inline[1]))
            for field in self.get_model_fields(inline[0]):
                try:
                    field_instances.append(
                        [field[0], FieldInstance(request, field[1],  "%s.%s" % (inline[0].__name__, field[0]), getattr(iitem, field[0]))])
                except AttributeError:
                    pass

        for field in fields:
            try:
                field_instances.append([field[0], FieldInstance(request, field[1], "%s.%s" % (MODELS[request.match_info['model']].__name__, field[0]), getattr(item, field[0]))])
            except AttributeError:
                pass
        return {
            'model': request.match_info['model'],
            'pk': request.match_info['id'],
            'item': item,
            'fields': field_instances
        }

    @template('admin/add.html')
    @login_required()
    async def add_page(self, request):
        fields = inspect.getmembers(MODELS[request.match_info['model']].Admin, lambda e: isinstance(e, form.FormField))

        inlines = getattr(MODELS[request.match_info['model']].Admin, '__inline__', [])
        field_instances = []

        for inline in inlines:
            for field in self.get_model_fields(inline[0]):
                try:
                    field_instances.append(
                        [field[0], FieldInstance(request, field[1], "%s.%s" % (inline[0].__name__, field[0]))])
                except AttributeError:
                    pass

        for field in fields:
            try:
                field_instances.append([field[0], FieldInstance(request, field[1], "%s.%s" % (
                MODELS[request.match_info['model']].__name__, field[0]))])
            except AttributeError:
                pass

        return {
            'model': request.match_info['model'],
            'fields': field_instances
        }

@template('admin/index.html')
@login_required()
async def index(request):
    return {
        'models': MODELS
    }
