import aioweb.core
from aioweb.core.controller import before


def set_user(ctrl):
    ctrl.user = 'username'

def set_group(ctrl):
    ctrl.group = '%s group' % ctrl.user

class Page1Controller(aioweb.core.BaseController):

    def __init__(self, request):
        super().__init__(request)
        self._defaultLayout = 'base.html'

    async def index(self):
        return {'test': 'It works!', 'username': self.user, 'group': self.group}

    async def csrf(self):
        self.use_view('page1/index.html')
        return await self.index()

    async def private(self):
        pass


Page1Controller.before_action(set_user)
Page1Controller.before_action(set_group)
