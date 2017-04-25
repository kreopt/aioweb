from aioweb.core.model import Model


class Permission(Model):
    __guarded__ = ['id']

    def users(self):
        pass

    def groups(self):
        pass

    def __str__(self):
        return self.name
