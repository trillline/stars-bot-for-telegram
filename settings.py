
from data_redis import RAMdata
from database.dao.dao import SettingDAO
from database.db_settings import connection
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, delete
from database.models import Setting
from logs.logging_bot import logger

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

    if not any(k["key"] == "star_course"  for k in settings):
        await SettingDAO.add(session, key="star_course", value="1.42")
        logger.info("star_course -> PostgreSQL (DEFAULT)")

    if not any(k["key"] == "price_premium_3" for k in settings):
        await SettingDAO.add(session, key="price_premium_3", value="1150")
        logger.info("price_premium_3 -> PostgreSQL (DEFAULT)")

    if not any(k["key"] == "price_premium_6" for k in settings):
        await SettingDAO.add(session, key="price_premium_6", value="1550")
        logger.info("price_premium_6 -> PostgreSQL (DEFAULT)")

    if not any(k["key"] == "price_premium_12" for k in settings):
        await SettingDAO.add(session, key="price_premium_12", value="2500")
        logger.info("price_premium_12 -> PostgreSQL (DEFAULT)")

    if not any(k["key"] == "cryptobot_fee" for k in settings):
        await SettingDAO.add(session, key="cryptobot_fee", value="2")
        logger.info("cryptobot_fee -> PostgreSQL (DEFAULT)")

    stars_course_redis = await RAMdata.get("star_course")
    price_premium_3 = await RAMdata.get("price_premium_3")
    price_premium_6 = await RAMdata.get("price_premium_6")
    price_premium_12 = await RAMdata.get("price_premium_12")
    cryptobot_fee = await RAMdata.get("cryptobot")

    if not stars_course_redis:
        await get_from_db_set_to_redis(session, "star_course")
        logger.info("star_course -> Redis (from PostgreSQL, set_settings)")
    if not price_premium_3:
        await get_from_db_set_to_redis(session, "price_premium_3")
        logger.info("price_premium_3 -> Redis (from PostgreSQL, set_settings)")
    if not price_premium_6:
        await get_from_db_set_to_redis(session, "price_premium_6")
        logger.info("price_premium_6 -> Redis (from PostgreSQL, set_settings)")
    if not price_premium_12:
        await get_from_db_set_to_redis(session, "price_premium_12")
        logger.info("price_premium_12 -> Redis (from PostgreSQL, set_settings)")
    if not cryptobot_fee:
        await get_from_db_set_to_redis(session, "cryptobot_fee")
        logger.info("cryptobot_fee -> Redis (from PostgreSQL, set_settings")



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
    return str(setting)[1:].strip('\'')

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