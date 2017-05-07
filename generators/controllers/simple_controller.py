import aioweb.core
from aioweb.core.controller.decorators import default_layout, before_action, template, layout, redirect_on_success


@default_layout('base.html')
class CLASS(aioweb.core.Controller):
    pass
