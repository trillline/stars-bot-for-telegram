from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def fee_settings_step1_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        #[InlineKeyboardButton(text="Cardlink", callback_data="change_fee_cardlink")],
        [InlineKeyboardButton(text="CryptoBot", callback_data="change_fee_cryptobot")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_panel")]
    ])

def fee_settings_step2_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_change_fee")]
    ])

