from typing import List, Any, Dict
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, Payment, Referral, Setting
from sqlalchemy.orm import class_mapper
import logging

class BaseDAO: # универсальный базовый класс для работы с таблицами
    model = None  # Устанавливается в дочернем классе

    @classmethod
    async def add(cls, session: AsyncSession, **values): # добавление одной записи в model(таблицу)
        # Добавить одну запись
        new_instance = cls.model(**values) # создание одного инстанса
        session.add(new_instance) # добавление в сессию данных
        logging.info("Запись добавлена в сессию")
        try:
            logging.info("Запись успешно закомитена")
            await session.commit() # коммит
        except SQLAlchemyError as e:
            await session.rollback() # роллбек при ошибке
            raise e # пробрасываем далее исключение
        finally:
            await session.close()
        return new_instance

    @classmethod
    async def add_many(cls, session: AsyncSession, instances: List[Dict[str, Any]]): # добавление нескольких записей в model(таблицу)
        new_instances = [cls.model(**values) for values in instances]
        session.add_all(new_instances)
        try:
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
        return new_instances

