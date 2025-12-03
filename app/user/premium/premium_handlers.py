import asyncio
import uuid
from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from config import load_config
import app.user.premium.premium_keyboard as kb
import app.user.states as states

from app.middlewares.user_middleware import GlobalStateMiddleware

from settings import get_setting
import payments.cryptobot_payments as Cryptobot
from database.requests import add_payment, get_user_referrer_balance, update_referrer_balance, give_referrer_reward
from payments.cryptobot_check_payment import check_payment_loop
from payments.cryptobot_payments import get_current_rate
from logs.logging_bot import logger
from fragment.fragment_queue_buying import purchase_queue
import payments.crystalpay_payments as Crystalpay

config = load_config()

premium_router = Router()
premium_router.message.middleware(GlobalStateMiddleware())
premium_router.callback_query.middleware(GlobalStateMiddleware())


@premium_router.callback_query(F.data == "choose_premium")
async def choose_owner(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

    await state.clear()
    await state.update_data(type_purchase='premium')

    await callback.message.answer_photo(photo=config.visuals.photo_file,caption="""
👑<b>Покупка премиум-подписки</b>

🔎Выберите, кому будем отправлять подписку:""",
                                        reply_markup=kb.Choose_owner_keyboard,
                                        parse_mode="HTML")


@premium_router.callback_query(F.data == "choose_premium_package")
async def choose_package(callback: CallbackQuery, state: FSMContext, bot: Bot):

    if not callback.from_user.username:
       await bot.answer_callback_query(callback_query_id=callback.id, show_alert=True,
                                        text="У вас не задан @username.\nПожалуйста, задайте его в настройках аккаунта Telegram.")
       return
    await callback.answer()
    data = await state.get_data()
    if "username" not in data:
        await state.update_data(username=callback.from_user.username)

    data = await state.get_data()
    await callback.message.edit_caption(caption=f"""
👑<b>Покупка премиум-подписки</b>

👤<b>Получатель:</b> @{data['username']} 

🔎Выберите количество месяцев подписки для покупки:""",
                                        reply_markup= await kb.choose_package_keyboard(),
                                        parse_mode="HTML")
    await state.set_state(states.PremiumPurchase.month)




@premium_router.message(states.PremiumPurchase.username)

async def input_user_owner_stars(message: Message, state:FSMContext):

    username_own_stars = message.text[1:] if message.text[0] == '@' else message.text

    if len(username_own_stars) >= 4 and \
        all(map(lambda x: ord(x.lower()) in [i for i in range(ord('a'),ord('z')+1)]+[i for i in range(ord('0'),ord('9')+1)]+[ord('_')],username_own_stars)):

        await state.update_data(username=message.text.replace("@", ''))  # ПОМЕНЯТЬ НА СОХРАНЕНИЕ В БД И ОЧИСТКУ ИЗ ОП
        await message.answer_photo(photo=config.visuals.photo_file,
                                   caption=f"⭐<b>Покупка премиум-подписки</b>\n"
                                           f"\n👤<b>Username:</b> @{username_own_stars} \n"
                                           f"⚠️<b>Проверьте username перед покупкой!</b>",
                                   reply_markup=kb.accept_entered_username_stars_keyboard,
                                   parse_mode="HTML")
    else:
        await message.answer_photo(photo = config.visuals.photo_file,
                                   caption=f"❌<b>Недопустимый username</b>\n"
                                          f"\n🔎<b>Введите username пользователя</b>, которому будем дарить звёзды:\n"
                                          f"—Пример: @{message.from_user.username}",
                                   reply_markup=kb.Go_back_to_choose_owner_keyboard,
                                   parse_mode="HTML")




@premium_router.callback_query(F.data == "buy_premium_to_other_user")
async def choose_other_user_owner(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    await callback.message.edit_caption(caption=f"""
👑<b>Покупка премиум-подписки</b>

🔎Введите username пользователя, которому будем дарить подписку:
— Пример: @{callback.from_user.username}""",
                                        reply_markup=kb.Go_back_to_choose_owner_keyboard,
                                        parse_mode="HTML")
    await state.set_state(states.PremiumPurchase.username)





@premium_router.callback_query(F.data.startswith("premium_month"))
async def entered_premium_month(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    await state.set_state(None)
    if callback.data.split("_")[-1] != "back":
        await state.update_data(month = int(callback.data.split("_")[-1]))
    data = await state.get_data()
    username = data.get("username")
    months = data.get("month")
    price = await get_setting(f"price_premium_{months}") # приходит в виде строки


    await callback.message.edit_caption(caption=f"""
👑Выбранная подписка: <b> Премиум на {months} мес.</b>

👤<b>Получатель:</b> @{username}

💰<b>Стоимость:</b> {price} ₽

⚠️<b><u>Убедитесь что у @{username} отсутствует премиум-подписка.</u></b>

👇Выберите метод оплаты👇""",
                                        reply_markup=await kb.payment_methods_premium_keyboard(),
                                        parse_mode="HTML")





@premium_router.callback_query(F.data == "cryptobot_payment_premium")
async def payment_to_cryptobot_for_purchasing_premium(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()

    await state.set_state(None)
    await state.update_data(type_payment="cryptobot")
    data = await state.get_data()
    months = data.get("month")
    price = await get_setting(f"price_premium_{months}")  # приходит в виде строки
    fee = await get_setting("cryptobot_fee") # приходит в виде строки
    amount_with_fee = float(price) + (float(price) * (int(fee)/100))
    created_invoice = await Cryptobot.create_invoice(amount=amount_with_fee, description=f"👑 Покупка премиума {months} мес. в StarsCAPITAN")
    pay_url = created_invoice.get("payment_url")
    invoice_id = created_invoice.get("invoice_id")

    data_payment = {"payment_method": "cryptobot", "cost": float(price), "fee": int(fee),
                    "total_cost": amount_with_fee,
                    "sender_id": callback.from_user.id, "product": "premium", "amount": int(data["month"]),
                    "invoice_id": invoice_id, "recipient_username":data["username"]}

    await add_payment(data=data_payment)  # добавляем в БД данные о платеже

    asyncio.create_task(check_payment_loop(invoice_id=invoice_id, user_id=callback.from_user.id, bot=bot,
                                           product="premium", username=data["username"], amount_product=data["month"]))  # проверка платежа



    await callback.message.edit_caption(caption=f"""
👑Для покупки премиум-подписки на {months} мес:

<b>1. Нажмите кнопку "Оплатить Cryptobot"</b>
<b>2. Выберите криптовалюту на открывшейся странице</b>
<b>3. Завершите оплату</b>

💡Номер заказа: {invoice_id}
👤Получатель: @{data['username']}
💵Сумма к оплате: {price}₽
⚠️Комиссия кассы: {fee}% 

✅ После оплаты бот получит оповещение и автоматически обработает заказ""",
                                        reply_markup=kb.cryptobot_premium_keyboard(pay_url),
                                        parse_mode="HTML")


@premium_router.callback_query(F.data == "referrer_balance_payment_premium")
async def payment_to_ref_balance_for_purchasing_premium(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    user_id = callback.from_user.id
    data = await state.get_data()

    months = data["month"]
    price = await get_setting(key=f"price_premium_{months}")

    usdt_to_rub = await get_current_rate("USDT", "RUB")  # находим актуальный курс доллара
    result = await get_user_referrer_balance(user_id=callback.from_user.id)
    balance = float(result) * usdt_to_rub
    recipient_username = data["username"]

    if balance >= int(price):

        order_number = uuid.uuid4().hex[:16]
        data_payment = {"payment_method": "referrer_balance", "cost": int(price), "fee": 0,
                        "total_cost": int(price),
                        "sender_id": user_id, "product": "stars", "amount": int(months),
                        "invoice_id": order_number,
                        "recipient_username": recipient_username, "status":"paid"}
        await add_payment(data=data_payment)  # добавляем в БД данные о платеже
        new_balance = round((balance - int(price)) / usdt_to_rub, 4)
        await update_referrer_balance(user_id=callback.from_user.id,
                                      new_balance=new_balance)

        await purchase_queue.put(
            {"username": recipient_username, "amount": int(months), "product": "premium", "invoice_id": order_number,
             "bot": bot, "admin_message":False})
        await callback.message.edit_caption(caption=f"✅ <b>Оплата прошла успешно.</b>\n\n👑 Номер заказа: {order_number}\nВозможны задержки до 5 минут.",
                                            parse_mode="HTML")
    else:

        await callback.message.edit_caption(caption=f"❌ <b>Недостаточно средств на балансе.</b>\n\n💵 Приглашайте друзей и зарабатывайте с их покупок.",
                                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                                [InlineKeyboardButton(text="🔙 Назад", callback_data="premium_month_back")]
                                            ]),
                                            parse_mode="HTML")


@premium_router.callback_query(F.data == "crystalpay_payment_premium")
async def payment_to_crystalpay_for_purchasing_premium(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()

    await state.set_state(None)
    await state.update_data(type_payment="crystalpay")
    data = await state.get_data()
    months = data.get("month")
    price = await get_setting(f"price_premium_{months}")  # приходит в виде строки
    fee = await get_setting("crystalpay_fee")  # приходит в виде строки
    created_invoice = await Crystalpay.create_invoice(amount=float(price),
                                                    sender_user_id=callback.from_user.id,
                                                      recipient_username=data.get("username"),
                                                      product="premium",
                                                      amount_prod=months)
    if created_invoice.get("status") == 200 and not created_invoice.get("error"):
        pay_url = created_invoice.get("payment_url")
        invoice_id = created_invoice.get("invoice_id")

        data_payment = {"payment_method": "crystalpay", "cost": float(price), "fee": int(fee),
                        "total_cost": float(price),
                        "sender_id": callback.from_user.id, "product": "premium", "amount": int(data["month"]),
                        "invoice_id": invoice_id, "recipient_username": data["username"]}

        await add_payment(data=data_payment)  # добавляем в БД данные о платеже

        asyncio.create_task(check_payment_loop(invoice_id=invoice_id, user_id=callback.from_user.id, bot=bot,
                                               product="premium", username=data["username"],
                                               amount_product=data["month"]))  # проверка платежа

        await callback.message.edit_caption(caption=f"""
👑Для покупки премиум-подписки на {months} мес:
    
<b>1. Нажмите кнопку "Оплатить СБП"</b>
<b>2. Выберите криптовалюту на открывшейся странице</b>
<b>3. Завершите оплату</b>
    
💡Номер заказа: {invoice_id}

👤Получатель: @{data['username']}
💵Сумма к оплате: {price}₽ 
    
✅ После оплаты бот получит оповещение и автоматически обработает заказ""",
                                            reply_markup=kb.crystalpay_premium_keyboard(pay_url),
                                            parse_mode="HTML")
    else:
        logger.info(f"Invoice errors: {created_invoice.get('errors')}")
        await callback.message.edit_caption(caption=f"<b>😔 Что-то пошлое не так...</b>\n"
                                                    f"\nПопробуйте создать заказ заново.",
                                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                                [InlineKeyboardButton(text="🏠 На главное меню",
                                                                      callback_data="to_main_menu")]
                                            ]),
                                            parse_mode="HTML")

@premium_router.callback_query(F.data=="sbp_card_payment_premium")
async def payment_to_sbp_card_for_purchasing_premium(callback: CallbackQuery, state:FSMContext, bot: Bot):
    await callback.answer()

    await state.set_state(None)
    data = await state.get_data()
    months = data.get("month")
    recipient_username = data.get("username")

    bot_url = config.links.support_link
    text = f"#БезКомиссии.\n👑 Товар: {months} мес. премиум-подписки\n👤 Получатель: @{recipient_username}\nКак оплатить?"

    await callback.message.edit_caption(caption=f"""
👑Для покупки премиум-подписки на {months} мес:

<b>1. Нажмите на следующее сообщение, чтобы скопировать или просто скопируйте:</b>

<code>{text}</code>

<b>2. Нажмите кнопку "Оплатить СБП"</b>
<b>3. Отправьте скопированное сообщение.</b>
<b>4. Получите реквизиты для оплаты</b>
<b>5. Оплатите и ожидайте зачисления премиум-подписки.</b>

        """,
                                        reply_markup=kb.sbp_card_premium_keyboard(bot_url),
                                        parse_mode="HTML")
