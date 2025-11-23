from config import load_config
import redis
from logs.logging_bot import logger

config = load_config()

# СТАТИЧЕСКИЙ КЛАСС ДЛЯ РАБОТЫ С ДАННЫМИ ИЗ ОПЕРАТИВНОЙ ПАМЯТИ С ПОМОЩЬЮ СЕРВЕРА REDIS

class RAMdata:

    data_redis = redis.asyncio.Redis(host=config.redis.host, port=config.redis.port, db=config.redis.db_data)

    @staticmethod
    async def set(key: str, value, ttl = None):
        await RAMdata.data_redis.set(key, value, ttl)
        logger.info(f"Key {key} was successful added in Redis")

    @staticmethod
    async def get(key: str):
       data = await RAMdata.data_redis.get(key)
       logger.info(f"Key {key} was successful received in Redis")
       return data

    @staticmethod
    async def delete(*keys):
        await RAMdata.data_redis.delete(*keys)
        logger.info(f"Key {keys} was successful deleted from Redis")

    @staticmethod
    async def exists(key: str):
        exists_data = await RAMdata.data_redis.exists(key)
        logger.info(f"Existing data about key {key} was successful gotten ")
        return exists_data