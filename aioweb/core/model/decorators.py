def cursor(fn):
    async def decorated(self, *args, **kwargs):
        async with self.db.pool.acquire() as conn:
            async with conn.cursor() as cur:
                self.cursor = cur
                res = await fn(self, *args, **kwargs)
                self.cursor = None
                return res

    return decorated
