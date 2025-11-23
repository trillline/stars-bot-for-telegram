from config import load_config
from aiogram import Bot

config = load_config()

async def notify_admin_about_payment(invoice_id,username_recipient, product, amount, bot: Bot, error_fragment: bool = False):
    if product == "stars":
        purchase = f"{amount} звёзд"
    else:
        purchase = f"{amount} мес. премиум-подписки"
    text = f"Номер заказа: {invoice_id}\nПолучатель: @{username_recipient}\nТовар: {purchase}\n"
    if error_fragment:
        text = "Fragment Error\nТребуется ручная отправка заказ\n\n" + text
    await bot.send_message(chat_id=config.bot.admin_id,text=text)
