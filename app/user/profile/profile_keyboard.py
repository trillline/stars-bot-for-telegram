from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

profile_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Назад", callback_data="to_main_menu")]
])