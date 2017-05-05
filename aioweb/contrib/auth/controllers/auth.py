from aiohttp import web

import aioweb.core
from aioweb.contrib.auth import authenticate, AuthError, forget_user
from aioweb.core.controller.decorators import default_layout
from aioweb.conf import settings
from aioweb.util import import_controller, awaitable


@default_layout('base.html')
class AuthController(aioweb.core.Controller):
    def redirect_authenticated(self):
        if self.request.user.is_authenticated():
            redirect_url = self.request.query.get('redirect_to')
            if not redirect_url:
                redirect_url = getattr(settings, 'AUTH_PRIVATE_URL', '/')
            raise web.HTTPFound(redirect_url)

    async def index(self):
        self.redirect_authenticated()
        if hasattr(settings, 'AUTH_INDEX_HANDLER'):
            ctrl, action = getattr(settings, 'AUTH_INDEX_HANDLER').split('#')
            ctrl_class, ctrl_class_name = import_controller(ctrl)
            hdlr = getattr(ctrl_class, action)
            return await awaitable(hdlr(self))

    async def login(self):
        data = await self.request.post()
        try:
            await authenticate(self.request, data.get('username'), data.get('password'), remember=True)
        except AuthError as e:
            if self.request.is_ajax():
                raise web.HTTPForbidden(reason=str(e))
            else:
                self.flash['AUTH_ERROR'] = str(e)
                raise web.HTTPFound(self.url_for('index'))

        self.redirect_authenticated()
        raise web.HTTPForbidden(reason='Unauthenticated')  # This should not happen

    async def logout(self):
        await forget_user(self.request)
        raise web.HTTPFound(getattr(settings, 'AUTH_GUEST_URL', '/'))
