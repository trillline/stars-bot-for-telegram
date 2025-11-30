from aiohttp import web
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import hashlib
import hmac
import aiohttp

from config import load_config
from database.requests import update_status_payment, give_referrer_reward

from logs.logging_bot import logger
from fragment.fragment_queue_buying import purchase_queue

config = load_config()

async def crystalpay_webhook(request):
    data = await request.json()
    logger.info("CATCH WEBHOOK")
    bot: Bot = request.app["bot"]

    invoice_id = data.get("id")
    signature = data.get("signature")
    status = data.get("state")
    extra = data.get("extra").split('!') # восклицательный знак sep потому что username может содержать _
    sender_user_id = extra[0]
    recipient_username = extra[1]
    product = extra[2]
    amount_product = extra[3]
    amount_rub = float(data.get("rub_amount"))

    hash_string = f"{invoice_id}:{config.crystalpay.salt}"
    computed_hash = hashlib.sha1(hash_string.encode()).hexdigest()

    if hmac.compare_digest(computed_hash, signature):
        if status == "payed":
            logger.info(f"Получен callback с оплатой. Invoice_id: {invoice_id}")
            await update_status_payment(invoice_id=invoice_id, status="paid")

            await give_referrer_reward(referral_id=int(sender_user_id), amount=amount_rub)

            await bot.send_message(chat_id=sender_user_id,
                                   text="✅ Оплата прошла успешно.\n\n⭐ Заказ уже обрабатывается.\nВозможны задержки до 5 минут.",
                                   reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                       [InlineKeyboardButton(text="ОК", callback_data="to_main_menu")]
                                   ]))
            await purchase_queue.put(
                {"username": recipient_username, "amount": amount_product, "product": product, "invoice_id": invoice_id,
                 "bot": bot})

    return web.Response(status=200)


async def run_webhook_server(bot):
    app = web.Application()
    app["bot"] = bot

    app.router.add_post("/crystalpay/invoice/", crystalpay_webhook)

    # Запуск сервера
    logger.info("WEBHOOK SERVER START 0.0.0.0:8080")

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()

    while True:
        await asyncio.sleep(3600)


