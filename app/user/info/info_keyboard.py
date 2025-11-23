from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


Information_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📙 Правила", url='https://telegra.ph/Pravila-ispolzovaniya-servisa-StarsCAPITAN-11-08'), InlineKeyboardButton(text="🔒 Конфиденциальность", url='https://telegra.ph/Politika-konfidencialnosti-servisa-StarsCAPITAN-11-08')],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="to_main_menu")]
])