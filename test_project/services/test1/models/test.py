import aioweb


class Model(aioweb.core.Model):
    __database__ = 'default'

    def action(self):
        return self.db.first('select 1 as val', column=0)
