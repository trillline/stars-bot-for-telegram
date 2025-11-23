from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_panel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💵 Настроить цены", callback_data="admin_change_price")],
        [InlineKeyboardButton(text="🤑 Настроить комиссию", callback_data="admin_change_fee")],
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="👀 Проверить заказ", callback_data="admin_check_order")],
        [InlineKeyboardButton(text="⚙️ Технический режим", callback_data="admin_tech_mode")],
        [InlineKeyboardButton(text="⬅️ В меню", callback_data="to_main_menu")]
    ])