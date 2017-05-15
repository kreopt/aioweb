from orator.orm import has_many, belongs_to_many

from aioweb.core.model import Model, mutator, accessor
from passlib.handlers.sha2_crypt import sha256_crypt
from aioweb.contrib.auth.models import permission
from aioweb.contrib.auth.models import group


class AbstractUser(object):
    def is_authenticated(self):
        return False


class User(Model, AbstractUser):
    __guarded__ = ['id']
    __hidden__ = ['password']

    def __init__(self, _attributes=None, **attributes):
        if 'password' in attributes:
            attributes['password'] = User.hash_password(attributes['password'])
        super().__init__(_attributes, **attributes)

    @staticmethod
    def hash_password(value):
        # TODO: configurable hash type
        return sha256_crypt.hash(value)

    @mutator
    def password(self, value):
        self.set_raw_attribute('password', User.hash_password(value))

    def can(self, permission):
        # TODO: check it
        return self.permissions.has(permission).get()  # or self.groups.perimissions.has(permission).get()

    @belongs_to_many('user_permissions')
    def permissions(self):
        return permission.Permission

    @belongs_to_many('user_groups')
    def groups(self):
        return group.Group

    @accessor
    def username(self):
        return self.phone if self.phone else self.email

    def __str__(self):
        return self.username
