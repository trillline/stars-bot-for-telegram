from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import load_config

config = load_config()

def get_main_menu_keyboard(telegram_id):
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="⭐️ Звёзды", callback_data="choose_stars_owner"),
        InlineKeyboardButton(text="👑 Премиум", callback_data="choose_premium")
    )
    builder.row(
        InlineKeyboardButton(text="👥 Реферальная программа", callback_data="show_referral_system")
    )
    builder.row(
        InlineKeyboardButton(text="🎩 Профиль", callback_data="show_profile")
    )
    builder.row(
        InlineKeyboardButton(text="📣 Новостной канал", url=config.links.news_link)
    )
    builder.row(
        InlineKeyboardButton(text="🆘 Поддержка", url=config.links.support_link),
        InlineKeyboardButton(text="ℹ️ Информация", callback_data="info")
    )
    if telegram_id == config.bot.admin_id:
        builder.row(
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="admin_panel")
        )
    return builder.as_markup()