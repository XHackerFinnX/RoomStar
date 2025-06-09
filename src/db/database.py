import asyncpg

from config import config

class DataBase:
    def __init__(self):
        self._pool = None

    async def connect(self):
        if not self._pool:
            self._pool = await asyncpg.create_pool(
                host=config.POSTGRESQL_HOST.get_secret_value(),
                database=config.POSTGRESQL_DATABASE.get_secret_value(),
                user=config.POSTGRESQL_USER.get_secret_value(),
                password=config.POSTGRESQL_PASSWORD.get_secret_value(),
                port=config.POSTGRESQL_PORT.get_secret_value(),
            )
        return self._pool

    async def close(self):
        if self._pool:
            await self._pool.close()
            self._pool = None