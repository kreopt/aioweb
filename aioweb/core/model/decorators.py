def cursor(fn):
    async def decorated(self, *args, **kwargs):
        async with self.db.pool.acquire() as conn:
            async with self.db._get_cursor(conn) as cur:
                self.cursor = cur
                res = await fn(self, *args, **kwargs)
                self.cursor = None
                return res

    return decorated
