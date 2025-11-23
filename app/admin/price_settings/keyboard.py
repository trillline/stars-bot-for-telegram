from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def price_settings_step1_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Курс звёзд", callback_data="admin_change_star_price")],
        [InlineKeyboardButton(text="👑 Премиум 3 мес.", callback_data="admin_change_premium_price_3")],
        [InlineKeyboardButton(text="👑 Премиум 6 мес.", callback_data="admin_change_premium_price_6")],
        [InlineKeyboardButton(text="👑 Премиум 12 мес.", callback_data="admin_change_premium_price_12")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_panel")]
    ])

def price_settings_step2_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_change_price")]
    ])

def price_settings_step3_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_change_price")]
    ])