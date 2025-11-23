from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def broadcast_text():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Нет текста", callback_data="no_text_broadcast")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_panel")]
    ])

def broadcast_photo():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Нет фото", callback_data="no_photo_broadcast")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_broadcast")]
    ])

def broadcast_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Купить звёзды", callback_data="broadcast_button_buystars"), InlineKeyboardButton(text="👑 Купить премиум", callback_data="broadcast_button_buypremium")],
        [InlineKeyboardButton(text="❌ Нет кнопки", callback_data="broadcast_button_no")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="no_text_broadcast")]
    ])

def broadcast_complete():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👀 Просмотреть рассылку", callback_data="broadcast_checking")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="no_photo_broadcast")]
    ])

def get_button(button: str, status: str = None):

    if status == "fake":
        callback_status = "_fake"
    else:
        callback_status = ''

    if button == "buypremium":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👑 Купить премиум", callback_data="choose_premium" + callback_status)]
        ])
    elif button == "buystars":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⭐ Купить звёзды", callback_data="choose_stars_owner" + callback_status)]
        ])
    else:
        return None

