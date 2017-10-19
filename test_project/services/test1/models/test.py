import aioweb


class Model(aioweb.core.Model):

    async def action(self):
        return {
            'test': await self.db('test').first('select id from test', column='id'),
            'default': await self.db.first('select id from test', column='id')
        }
