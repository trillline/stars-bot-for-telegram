from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from settings import get_setting
import urllib.parse

choose_stars_owner_keyboard= InlineKeyboardMarkup(inline_keyboard= [
    [InlineKeyboardButton(text="🫵 Себе",  callback_data=f"choose_stars_package_me"),InlineKeyboardButton(text="👤 Другому", callback_data="buy_stars_to_other_user")],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="to_main_menu")]
])


#callback названы суммой звёзд для их более лёгкой обработки (см. хэндлер в stars_handlers.py)
async def choose_amount_stars_keyboard():
    setting = await get_setting("star_course")
    sc = float(setting) # StarCourse
    return InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=f"⭐50 ({round(50*sc,1)}₽)  ", callback_data="buy_stars_fix_50"), InlineKeyboardButton(text=f"⭐100 ({round(100*sc,1)}₽)", callback_data="buy_stars_fix_100")],
    [InlineKeyboardButton(text=f"⭐150 ({round(150*sc,1)}₽)", callback_data="buy_stars_fix_150"), InlineKeyboardButton(text=f"⭐250 ({round(250*sc,1)}₽)", callback_data="buy_stars_fix_250")],
    [InlineKeyboardButton(text=f"⭐350 ({round(350*sc,1)}₽)", callback_data="buy_stars_fix_350"), InlineKeyboardButton(text=f"⭐500 ({round(500*sc,1)}₽)", callback_data="buy_stars_fix_500")],
    [InlineKeyboardButton(text=f"⭐750 ({round(750*sc,1)}₽)", callback_data="buy_stars_fix_750"), InlineKeyboardButton(text=f"⭐1000 ({round(1000*sc,1)}₽)", callback_data="buy_stars_fix_1000")],
    [InlineKeyboardButton(text=f"⭐1500 ({round(1500*sc,1)}₽)",callback_data="buy_stars_fix_1500"), InlineKeyboardButton(text=f"⭐2500 ({round(2500*sc,1)}₽)", callback_data="buy_stars_fix_2500")],
    [InlineKeyboardButton(text=f"⭐5000 ({round(5000*sc,1)}₽)", callback_data="buy_stars_fix_5000"), InlineKeyboardButton(text=f"⭐10000 ({round(10000*sc,1)}₽)", callback_data="buy_stars_fix_10000")],
    [InlineKeyboardButton(text="📝 Указать своё количество", callback_data="choose_own_amount_stars")],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="choose_stars_owner")]
])

Input_username_stars_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Назад", callback_data="choose_stars_owner")]
])


accept_entered_username_stars_keyboard=InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"choose_stars_package_other")],
    [InlineKeyboardButton(text="❌ Отменить", callback_data="buy_stars_to_other_user")]
])

async def payment_methods_stars_keyboard():
    cryptobot_fee = await get_setting("cryptobot_fee")
    crystalpay_fee = await get_setting("crystalpay_fee")
    return InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=f"💎 CryptoBot | {cryptobot_fee}% ", callback_data="cryptobot_payment_stars")],
    [InlineKeyboardButton(text="🇷🇺 СБП рубли | Без комиссии", callback_data="sbp_card_payment_stars")],
    [InlineKeyboardButton(text=f"🇷🇺 СБП рубли | {crystalpay_fee}%", callback_data="crystalpay_payment_stars")],
    [InlineKeyboardButton(text="👥 Реферальный баланс", callback_data="referrer_balance_payment_stars")],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="choose_stars_package")]
])

Input_amount_stars_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Назад", callback_data="choose_stars_package")]
])

def cryptobot_payment_keyboard(pay_url):
    return InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💳 Оплатить CryptoBot", url = pay_url)],
    [InlineKeyboardButton(text="🔙 Назад", callback_data='buy_stars_back')]
])

def crystalpay_payment_keyboard(pay_url):
    return InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💳 Оплатить СБП", url = pay_url)],
    [InlineKeyboardButton(text="🔙 Назад", callback_data='buy_stars_back')]
])

def sbp_card_payment_keyboard(bot_url):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить СБП", url=f"{bot_url}?start=sbp")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data='buy_stars_back')]
    ])
