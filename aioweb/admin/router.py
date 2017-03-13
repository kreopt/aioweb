from . import views

from aioweb.routes import Router


class AppRouter(Router):
    def setup(self):
        self.get('/', views.index, name='index')
        self.resource('{model:[a-z0-9_]+}', views.ModelAdmin())
