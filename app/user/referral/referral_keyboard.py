from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="👤 Мои рефералы", callback_data='check_referrals')],
    [InlineKeyboardButton(text="ℹ️ Подробности программы", callback_data="refsys_information")],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="to_main_menu")]
])

info = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Назад", callback_data="show_referral_system")]
])