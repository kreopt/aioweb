import aioweb


class Model(aioweb.core.Model):
    __database__ = 'default'

    def action(self):
        # self.db.connection('test').first('select 1 as val', column=0)
        return self.db.first('select 1 as val', column=0)
