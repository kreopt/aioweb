import aioweb.core
from aioweb.core.controller.decorators import default_layout


@default_layout('base.html')
class CLASS(aioweb.core.BaseController):
    pass
