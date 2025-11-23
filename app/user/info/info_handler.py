from aiogram import F, Router
from aiogram.types import CallbackQuery

import app.user.info.info_keyboard as kb

info_router = Router()

@info_router.callback_query(F.data == "info")
async def information(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_caption(caption=f"""
ℹ️<b>Информация</b>

Здесь вы можете ознакомиться с правилами использования сервиса и политикой конфиденциальности.
""",
                                        reply_markup= kb.Information_keyboard,
                                        parse_mode='HTML')