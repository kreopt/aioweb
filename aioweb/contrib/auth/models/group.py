from aioweb.core.model import Model


class Group(Model):
    __guarded__ = ['id']

    def users(self):
        pass

    def permissions(self):
        pass

    def can(self, permission):
        pass

    def __str__(self):
        return self.name
