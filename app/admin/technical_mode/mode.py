from aiogram import F, Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import load_config
import app.admin.technical_mode.keyboard as keyboard
import app.admin.states as st
from data_redis import RAMdata

technical_router = Router()
config = load_config()

@technical_router.callback_query(F.data == "admin_tech_mode")
async def set_mode(callback: CallbackQuery, bot: Bot):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await callback.message.answer(text="<b>🛠️ Панель перевода бота в технический режим </b>",
                                reply_markup = keyboard.technical_mode(),
                                parse_mode = "HTML")


@technical_router.callback_query(F.data == "technical_mode_on")
async def technical_mode_on(callback: CallbackQuery, bot: Bot):
    await RAMdata.set("global_mode", "mode_on")
    await bot.answer_callback_query(callback_query_id=callback.id,text="Технический режим: ON ✅", show_alert=True)

@technical_router.callback_query(F.data == "technical_mode_off")
async def technical_mode_off(callback: CallbackQuery, bot: Bot):
    await RAMdata.set("global_mode", "mode_off")
    await bot.answer_callback_query(callback_query_id=callback.id, text="Технический режим: OFF ❌", show_alert=True)