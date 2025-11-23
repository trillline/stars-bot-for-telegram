import asyncio
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


from payments.cryptobot_payments import get_invoice_info
from database.requests import update_status_payment, give_referrer_reward, update_fragment_id
from aiogram import Bot
from logs.logging_bot import logger
from notifications.notifications_admin import notify_admin_about_payment
import time


async def check_payment_loop(invoice_id: str, user_id: int, username: str,bot: Bot, product:str, amount_product):

    start_time = time.time()
    interval = 10  # 5 секунд
    timeout = 600 + 100 # 600 - timeout, 100 - запас
    logger.info(f"Проверка платежа {invoice_id}")
    while time.time() - start_time < timeout:

        invoice = await get_invoice_info(invoice_id)

        if invoice["success"]:
            logger.info(f"Прошло {time.time() - start_time} секунд. Статус: {invoice.get('status', 'error')}")
            if invoice["status"] == "paid":

                await update_status_payment(invoice_id=invoice_id,status= "paid")

                amount_rub = float(invoice["amount"])

                await give_referrer_reward(referral_id=user_id, amount=amount_rub)


                if product == "stars":
                    text = "⭐ Заказ уже обрабатывается.\nВозможны задержки до 5 минут."
                else:
                    text = "👑 Заказ уже обрабатывается. \nВозможны задержки до 5 минут."

                await bot.send_message(chat_id=user_id, text="✅ Оплата прошла успешно.\n\n"+text,
                                       reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                           [InlineKeyboardButton(text="ОК", callback_data="to_main_menu")]
                                    ]))

               # await purchase_queue.put({"username":username, "amount":amount_product, "product":product, "invoice_id":invoice_id, "bot":bot})
                await notify_admin_about_payment(invoice_id=invoice_id, username_recipient=username, product=product, amount=amount_product, bot=bot)
                return

            # 3️⃣ Истёк срок действия
            if invoice["status"] == "expired":
                await update_status_payment(invoice_id=invoice_id,status= "expired")
                return
        else:
            logger.info(f"Прошло {time.time() - start_time} секунд. Статус: {invoice.get('error', )}")

        await asyncio.sleep(interval)

    # 4️⃣ Оплата так и не пришла за время ожидания
    await update_status_payment(invoice_id, "timeout")
