from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def fee_settings_step1_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="CryptoBot", callback_data="change_fee_cryptobot")],
        [InlineKeyboardButton(text="CrystalPay", callback_data="change_fee_crystalpay")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_panel")]
    ])

def fee_settings_step2_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_change_fee")]
    ])

