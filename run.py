import asyncio
from logs.logging_bot import logger
from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage
import config as cnfg
import redis
from data_redis import RAMdata
from aiogram.fsm.storage.redis import RedisStorage


from app.main.main_handler import main_router
from app.user.premium.premium_handlers import premium_router
from app.user.stars.stars_handlers import stars_router
from app.user.profile.profile_handler import profile_router
from app.user.info.info_handler import info_router
from app.user.referral.referral_handlers import referral_router


from app.admin.admin_menu.menu import admin_menu_router
from app.admin.price_settings.price import price_settings_router
from app.admin.fee_settings.fee import  fee_settings_router
from app.admin.technical_mode.mode import technical_router
from app.admin.broadcast.broadcast_menu import broadcast_router
from app.admin.checking_order.check_order import checkOrder_router
from settings import set_default_settings

#from fragment.fragment_queue_buying import purchase_worker, purchase_queue

async def start_bot():

    config = cnfg.load_config()

    try:
        fsm_redis = redis.asyncio.Redis(host=config.redis.host, port=config.redis.port, db=config.redis.db_fsm)
        storage = RedisStorage(redis=fsm_redis)
        logger.info("Connection to Redis completed successfully")
    except Exception:
        logger.error(f"REDIS ERROR. STORAGE OF FSM STATES IS MemoryStorage() NOW")
        storage = MemoryStorage()

    bot = Bot(token=config.bot.bot_token)
    logger.info("Bot created")
    dp = Dispatcher(storage=storage)
    logger.info("Dispatcher created")

    dp.include_router(main_router)
    dp.include_routers(premium_router, stars_router, info_router, profile_router, referral_router)
    dp.include_routers(admin_menu_router, price_settings_router,
                       fee_settings_router, technical_router, broadcast_router, checkOrder_router)
    logger.info("DP included all routers")

    info = await bot.get_me()
    await RAMdata.set("bot_username", info.username)

    await set_default_settings()

    logger.info("\n START \n")

   # asyncio.create_task(purchase_worker())

   # await asyncio.gather(dp.start_polling(bot),     server_main())
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(start_bot())
    except (KeyboardInterrupt, SystemExit):
        logger.info("\n STOP \n")