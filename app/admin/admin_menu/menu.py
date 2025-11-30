from aiogram import F, Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from config import load_config
from app.admin.admin_menu.keyboard import admin_panel_keyboard
from data_redis import RAMdata
from logs.logging_bot import logger

admin_menu_router = Router()

config = load_config()

@admin_menu_router.callback_query(F.data == "admin_panel")
async def admin_panel_main(callback: CallbackQuery,state:FSMContext, bot: Bot):
    await bot.delete_message(callback.message.chat.id,callback.message.message_id)
    await state.set_state(None)
    logger.info(f"Переход в админ-панель. Пользователь: {callback.from_user.username}")
    text = "🫡 Приветствую на борту, Босс!\n\n⬇️ Возьмите управление на себя\n"
    tech_mode = await RAMdata.get("global_mode")
    if tech_mode == "mode_on":
        text += "\n<b>ТЕХНИЧЕСКИЙ РЕЖИМ ВКЛЮЧЕН</b>✅🛠️"
    await callback.message.answer_photo(caption=text,
                                photo=config.visuals.photo_file,
                                reply_markup=admin_panel_keyboard(),
                                parse_mode="HTML")
