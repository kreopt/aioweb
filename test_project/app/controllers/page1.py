import aioweb.core
from aioweb.core.controller.decorators import before_action, default_layout, template
from aioweb.middleware.csrf.decorators import csrf_exempt, csrf_protect, disable_csrf


async def set_user(ctrl):
    ctrl.user = 'username'

def set_group(ctrl):
    ctrl.group = '%s group' % ctrl.user

@before_action(set_user)
@before_action(set_group)
@disable_csrf()
# @authenticated(only=tuple(), exclude=tuple())
@default_layout('base.html')
class Page1Controller(aioweb.core.BaseController):

    @csrf_exempt
    async def index(self):
        return {'test': 'It works!', 'username': self.user, 'group': self.group}

    @csrf_protect
    @template('page1/index.html')
    async def csrf(self):
        return await self.index()

    # @private
    async def private(self):
        pass
