import aioweb


class Model(aioweb.core.Model):

    async def action(self):
        return {
            'test': await self.db('test').first('select 1 id'),
            'default': await self.db.first('select 2 id', column='id')
        }
