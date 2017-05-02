from aioweb.core.model import Model, mutator
from passlib.handlers.sha2_crypt import sha256_crypt


class AbstractUser(object):

    def is_authenticated(self):
        return False


class User(Model, AbstractUser):

    __guarded__ = ['id']

    def __init__(self, _attributes=None, **attributes):
        if 'password' in attributes:
            attributes['password'] = User.hash_password(attributes['password'])
        super().__init__(_attributes, **attributes)

    @staticmethod
    def hash_password(value):
        return sha256_crypt.hash(value)

    @mutator
    def password(self, value):
        #TODO: configurable hash type
        self.set_raw_attribute('password', User.hash_password(value))

    def can(self, permission):

        return False

    def __str__(self):
        return self.username

