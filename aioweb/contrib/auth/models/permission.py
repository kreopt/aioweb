from orator.orm import belongs_to_many

from aioweb.core.model import Model
from aioweb.contrib.auth.models import user
from aioweb.contrib.auth.models import group


class Permission(Model):
    __guarded__ = ['id']

    @belongs_to_many('user_permissions')
    def users(self):
        return user.User

    @belongs_to_many('user_groups')
    def groups(self):
        return group.Group

    def __str__(self):
        return self.name
