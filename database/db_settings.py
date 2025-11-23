
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from config import load_config
import logging


config = load_config() # загрузка конфига

DSN = f"postgresql+asyncpg://{config.db.user}:{config.db.password}@{config.db.host}:{config.db.port}/{config.db.db}" # Data Source Name
engine = create_async_engine(url=DSN,
                             pool_size=10,
                             max_overflow=20)

async_session = async_sessionmaker(engine) # инициализация фабрики сессий


def connection(method): # безопасное открытие и автоматическое закрытие сессии
    async def wrapper(*args, **kwargs):
        async with async_session() as session: # открываем сессию
            logging.info("Session is opened")
            try:
                return await method(*args, session=session, ** kwargs)
            except Exception:
                logging.info("Session error. Rollback.")
                await session.rollback() # откатываем сессию при ошибке
                raise Exception # поднимаем исключение дальше



    return wrapper


