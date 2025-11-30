
from data_redis import RAMdata
from database.dao.dao import SettingDAO
from database.db_settings import connection
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, delete
from database.models import Setting
from logs.logging_bot import logger


async def check_def_settings(session: AsyncSession, key:str,value:str, settings):
    if not any(k["key"] == key for k in settings):
        await SettingDAO.add(session=session, key=key, value=value)
        logger.info(f"{key} -> PostgreSQL (DEFAULT)")

    key_in_redis = await RAMdata.get(key)

    if not key_in_redis:
        await get_from_db_set_to_redis(session=session, key=key)
        logger.info(f"{key} -> Redis (from PostgreSQL, set_settings")


# При первом запуске бота и отсутствии записей в БД и в Redis-БД добавляет необходимые для работы бота настройки в обе БД
# Функция установки настроек по умолчанию
@connection
async def set_default_settings(session: AsyncSession):
    stmt = select(Setting.key, Setting.value)
    result = await session.execute(stmt)
    setting = result.all()

    settings = [
        {"key": z.key, "value": z.value}
        for z in setting
    ] # СПИСОК НАСТРОЕК

    await check_def_settings(session=session,key= "star_course", value="1.42", settings=settings)
    await check_def_settings(session=session,key= "price_premium_3", value="1150", settings=settings)
    await check_def_settings(session=session, key="price_premium_6", value="1550", settings=settings)
    await check_def_settings(session=session, key="price_premium_12", value="2500", settings=settings)
    await check_def_settings(session=session, key="cryptobot_fee", value="3", settings=settings)
    await check_def_settings(session=session, key="crystalpay_fee", value="0", settings=settings)



# вспомогательная функция для функции установки настроек по умолчанию, переносит данные из БД в Redis-сервер
async def get_from_db_set_to_redis(session: AsyncSession,key: str):
    stmt = select(Setting.value).filter_by(key=key)
    result = await session.execute(stmt)
    value = result.scalar_one_or_none()
    await RAMdata.set(key, value)


# функция получения нужной настройки БЕЗОПАСНО (т.е если нет в Redis, то ищем в PostgreSQL)

async def get_setting(key:str) -> str:
    setting = await RAMdata.get(key)
    if setting is None:
        db_setting_value = await get_setting_from_db(key=key)
        await RAMdata.set(key, db_setting_value)
        logger.info(f"got {key} from PostgreSQL")
        return db_setting_value
    logger.info(f"got {key} from Redis")
    return setting

# вспомогательная функция для функции получения настройки
@connection
async def get_setting_from_db(session: AsyncSession, key:str):
    stmt = select(Setting.value).filter_by(key=key)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

@connection
async def set_setting(session:AsyncSession, key:str, value:str):

    stmt_select = select(Setting).filter_by(key=key)
    result_select = await session.execute(stmt_select)
    setting_select = result_select.scalar_one_or_none()
    if setting_select is not None:
        stmt_del = delete(Setting).filter_by(key=key)
        await session.execute(stmt_del)
        await session.commit()

    await SettingDAO.add(session, key=key, value=value)

    await RAMdata.set(key=key, value=value)