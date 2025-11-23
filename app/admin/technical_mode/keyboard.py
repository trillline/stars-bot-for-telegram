from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def technical_mode():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Включить", callback_data="technical_mode_on"), InlineKeyboardButton(text="Выключить", callback_data="technical_mode_off")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_panel")]
    ])