from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
#from aiogram.utils.keyboard import InlineKeyboardBuilder
from settings import get_setting


Choose_owner_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🫵 Себе", callback_data="choose_premium_package"), InlineKeyboardButton(text="👤 Другому", callback_data="buy_premium_to_other_user")],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="to_main_menu")]
])

async def choose_package_keyboard():
    premium_3 = await get_setting("price_premium_3")
    premium_6 = await get_setting("price_premium_6")
    premium_12 = await get_setting("price_premium_12")
    return InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=f"👑 3 мес. ({premium_3}₽)", callback_data="premium_month_3")],
    [InlineKeyboardButton(text=f"👑 6 мес. ({premium_6}₽)", callback_data="premium_month_6")],
    [InlineKeyboardButton(text=f"👑 12 мес. ({premium_12}₽)", callback_data="premium_month_12")],
    [InlineKeyboardButton(text="🔙 Назад",callback_data="choose_premium")]
])

Go_back_to_choose_owner_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Назад", callback_data="choose_premium")]
])

accept_entered_username_stars_keyboard=InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"choose_premium_package")],
    [InlineKeyboardButton(text="❌ Отменить", callback_data="buy_premium_to_other_user")]
])

async def payment_methods_premium_keyboard():
    cryptobot_fee = await get_setting("cryptobot_fee")
    crystalpay_fee = await get_setting("crystalpay_fee")
    return InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=f"💎 CryptoBot | {cryptobot_fee}%", callback_data="cryptobot_payment_premium")],
    [InlineKeyboardButton(text="🇷🇺 СБП рубли | Без комиссии", callback_data="sbp_card_payment_premium")],
    [InlineKeyboardButton(text=f"🇷🇺 СБП рубли | {crystalpay_fee}% ", callback_data="crystalpay_payment_premium")],
    [InlineKeyboardButton(text="👥 Реферальный баланс", callback_data="referrer_balance_payment_premium")],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="choose_premium_package")]
])


def cryptobot_premium_keyboard(pay_url):
    return InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💳 Оплатить CryptoBot", url = pay_url)],
    [InlineKeyboardButton(text="🔙 Назад", callback_data='premium_month_back')]
])

def crystalpay_premium_keyboard(pay_url):
    return InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💳 Оплатить СБП", url = pay_url)],
    [InlineKeyboardButton(text="🔙 Назад", callback_data='premium_month_back')]
])

def sbp_card_premium_keyboard(bot_url):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить СБП", url=f"{bot_url}?start=sbp")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data='premium_month_back')]
    ])