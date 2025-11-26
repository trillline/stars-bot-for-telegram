from config import load_config
from aiogram import Bot
from payments.cryptobot_payments import get_current_rate
from fragment.fragment_api import check_balance
from logs.logging_bot import logger

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

async def notify_if_fragment_balance_is_not_enough(amount_fiat: float, bot: Bot):
    ton_to_rub = await get_current_rate(from_asset="TON", to_asset="RUB")
    ton_need = round(amount_fiat / ton_to_rub + 0.1,2)
    fragment_balance = await check_balance()
    logger.info(f"Fragment Balance: {fragment_balance}")
    if fragment_balance["status"] == 200:
        balance = round(float(fragment_balance["balance"]),2)
        if ton_need > balance:
            await bot.send_message(chat_id=config.bot.admin_id,text=f"⚠️ Недостаточно средств на кошельке.\n\nПокупка на {ton_need} TON. Не хватает {round(ton_need - balance,2)} TON")
