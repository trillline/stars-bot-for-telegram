from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

from data_redis import RAMdata
from aiogram import BaseMiddleware, Bot
from config import load_config

from logs.logging_bot import logger

config = load_config()

class GlobalStateMiddleware(BaseMiddleware):
    def __init__(self):
        pass

    # handler - функция которая должна обработать событие, @router.message(Command(start)) - например
    # event - входящее событие из Telegram, Message, CallbackQuery - например
    # data - внутренний DI (dependency injection) словарь Aiogram, в котором хранится:
    #   bot - объект Bot
    #   state - FSMContext
    #   event_from_user - пользователь
    #   event_chat - чат
    #   session - SQLAlchemy session (если вставить в Middleware)
    #   callback_query - если callback
    #   можно добавлять в словарь что угодно

    async def __call__(self, handler, event, data):
        state: FSMContext = data.get("state") # ДОБАВИТЬ ЛОГИКУ С СОСТОЯНИЕМ В КЛЮЧЕВЫХ ВАЖНЫХ МОМЕНТАХ (оплата, ожидание)
        bot: Bot = data.get("bot")
        # получаем информацию о техническом режиме
        mode = await RAMdata.get("global_mode")
        global_mode = str(mode)[1:].strip("\'") # превращаем байт-строку в нормальную строку
        logger.info(f"global_mode_key is {global_mode}")

        user_id = data["event_from_user"].id
        # --- ЛОГИКА ГЛОБАЛЬНОГО СОСТОЯНИЯ ---

        if global_mode == "mode_on" and user_id != config.bot.admin_id:

            await state.set_state(None)
            if isinstance(event, Message):
                target = event
            else:
                target = event.message
                await bot.delete_message(target.chat.id, target.message_id)

            await target.answer_photo(photo=config.visuals.photo_file,
                                 caption="<b>🛠️ Проводятся технические работы 🛠️ </b>\n"
                                         "\nПожалуйста, попробуйте зайти в этот раздел позже\n",
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                     [InlineKeyboardButton(text = "🏠 В главное меню", callback_data="to_main_menu")]
                                 ]),
                                parse_mode="HTML")
            return

        return await handler(event, data)