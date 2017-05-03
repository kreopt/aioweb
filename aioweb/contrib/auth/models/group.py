from orator.orm import belongs_to_many

from aioweb.core.model import Model
from aioweb.contrib.auth.models import permission
from aioweb.contrib.auth.models import user


class Group(Model):
    __guarded__ = ['id']

    @belongs_to_many('user_groups')
    def users(self):
        return user.User

    @belongs_to_many('group_permissions')
    def permissions(self):
        return permission.Permission

    def can(self, permission):
        # TODO: check it
        self.permissions().has(permission).get()

    def __str__(self):
        return self.name
