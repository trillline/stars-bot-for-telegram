import asyncio
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from payments.cryptobot_payments import get_invoice_info
from database.requests import update_status_payment, give_referrer_reward, update_fragment_id
from aiogram import Bot
from logs.logging_bot import logger
from notifications.notifications_admin import notify_admin_about_payment, notify_if_fragment_balance_is_not_enough
import time
from fragment.fragment_queue_buying import purchase_queue


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

                amount_rub = float(invoice["amount"])

                await notify_if_fragment_balance_is_not_enough(amount_fiat=amount_rub, bot=bot)

                await update_status_payment(invoice_id=invoice_id,status= "paid")

                await give_referrer_reward(referral_id=user_id, amount=amount_rub)


                if product == "stars":
                    text = "⭐ Заказ уже обрабатывается.\nВозможны задержки до 5 минут."
                else:
                    text = "👑 Заказ уже обрабатывается. \nВозможны задержки до 5 минут."

                await bot.send_message(chat_id=user_id, text="✅ Оплата прошла успешно.\n\n"+text,
                                       reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                           [InlineKeyboardButton(text="ОК", callback_data="to_main_menu")]
                                    ]))

                await purchase_queue.put({"username":username, "amount":amount_product, "product":product, "invoice_id":invoice_id, "bot":bot})
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
