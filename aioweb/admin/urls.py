import landing.views as views
from aioweb.render import template_view


def setup_url(router):
    router.add_get('/admin/', template_view('admin/index.html'), name='admin:index'),
    router.add_get('/admin/${model}/', template_view('admin/model_list.html'), name='admin:list'),
    router.add_get('/admin/${model}/${id}/', template_view('admin/model_edit.html'), name='admin:edit'),
    router.add_get('/admin/${model}/add/', template_view('admin/model_add.html'), name='admin:add'),
