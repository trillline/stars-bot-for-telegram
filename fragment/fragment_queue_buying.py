import asyncio
from aiogram import Bot

from config import load_config
from logs.logging_bot import logger
from database.requests import update_fragment_id
from fragment.fragment_api import buy_stars, buy_premium
from notifications.notifications_admin import notify_fragment_balance_is_not_enough

# глобальная асинхронная очередь
purchase_queue = asyncio.Queue()

config = load_config()
# для запуска в run.py создать фоновую задачу asyncio.create_task(purchase_worker())

# функция повторного запроса к фрагменту.
async def retry_request(recipient_username, amount_product, product, bot, invoice_id, admin_message=False):
    max_attempts = 4
    delay = 3  # сек
    was400 = False
    for attempt in range(1, max_attempts + 1):
        logger.info(f"Попытка №{attempt}")
        try:
            if product == "stars":
                result = await buy_stars(recipient_username, amount_product)
            elif product=="premium":
                result = await buy_premium(recipient_username, amount_product)
            else:
                logger.info(f"product = {product}, поэтому result = None")
                result = None
            logger.info(f"Result: {result}")
            if result.get("status") == 200:
                return result
            elif result.get("status") == 400 and result.get("error").startswith("Not enough funds for wallet"):
                 if not admin_message:
                    error = result.get("error")
                    balance = float(error[error.find("balance") + 10:error.find("TON") - 1])
                    transaction = float(error[error.rfind("total") + 7:error.rfind("TON") - 1])
                    need = round(transaction - balance, 2)
                    await notify_fragment_balance_is_not_enough(need=need, bot=bot)
                    admin_message = True
                 was400 = True
        except Exception as e:
            logger.info(f"Error {e}")
        logger.info(f"Сон {delay} сек.")
        if attempt != max_attempts: # чтобы по-просту не ждать последний сон
            await asyncio.sleep(delay)
        delay *= 2  # экспоненциальное увеличение задержки (5 -> 10 -> 20)\
    if was400:
        await purchase_queue.put(
            {"username": recipient_username, "amount": amount_product, "product": product,
             "invoice_id": invoice_id,
             "bot": bot, "admin_message": admin_message})
    raise RuntimeError("Fragment API не ответил после повторных попыток")

# функция обрабатывающая последовательно запросы к фрагменту
async def purchase_worker():
    while True:
        task = await purchase_queue.get()  # ждём задачу
        username = task.get("username")
        amount = task.get("amount")
        product = task.get("product")
        invoice_id = task.get("invoice_id")
        bot = task.get("bot")
        admin_message = task.get("admin_message")
        logger.info(f"ОЧЕРЕДЬ ЗАДАЧ: {purchase_queue}")
        logger.info(f"Выполняется задание в worker: {username} {amount} {product} {invoice_id}")
        try:
            result = await retry_request(recipient_username=username,amount_product= amount, product=product, bot=bot, invoice_id=invoice_id, admin_message=admin_message)
            if result.get("status") == 200 and result.get("success"):
                await update_fragment_id(invoice_id=invoice_id, fragment_id=result.get("id"))
        except RuntimeError as e:
            logger.info(f"Error: {e}")
        finally:
            purchase_queue.task_done()