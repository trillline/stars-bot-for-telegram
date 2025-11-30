import asyncio
import time
import uuid

from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from config import load_config
from logs.logging_bot import logger

import app.user.states as states
import app.user.stars.stars_keyboard as kb

from app.middlewares.user_middleware import GlobalStateMiddleware
from settings import get_setting # получаем setting

import payments.cryptobot_payments as Cryptobot
from database.requests import add_payment, get_user_referrer_balance, update_referrer_balance
from payments.cryptobot_check_payment import check_payment_loop

from payments.cryptobot_payments import get_current_rate

import payments.crystalpay_payments as Crystalpay

from fragment.fragment_queue_buying import purchase_queue

stars_router = Router()
config = load_config()

stars_router.message.middleware(GlobalStateMiddleware())
stars_router.callback_query.middleware(GlobalStateMiddleware())



@stars_router.callback_query(F.data == "choose_stars_owner")
async def choose_stars_owner(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

    await state.clear()
    await state.update_data(type_purchase="stars")

    await callback.message.answer_photo(photo=config.visuals.photo_file,
                                        caption="""
⭐<b>Покупка звёзд</b>

🔎Выберите, кому будем отправлять звёзды:""",
                                        reply_markup=kb.choose_stars_owner_keyboard,
                                        parse_mode="HTML")
    await state.set_state(states.StarsPurchase.username)





@stars_router.callback_query(F.data == "buy_stars_to_other_user")
async def input_username_to_purchase_stars(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_caption(caption=f"""
⭐<b>Покупка звёзд</b>

🔎Введите username пользователя, которому будем дарить звёзды:
—Пример: @{callback.from_user.username}
        """,
                                        reply_markup=kb.Input_username_stars_keyboard,
                                        parse_mode="HTML")




@stars_router.callback_query(F.data.startswith("choose_stars_package"))
async def choose_amount_stars(event: Message | CallbackQuery, state:FSMContext, bot: Bot):

    await state.set_state(state=None)
    if isinstance(event, CallbackQuery):
        target = event.message
        if not event.from_user.username:
            await bot.answer_callback_query(callback_query_id=event.id,show_alert=True, text="У вас не задан @username.\nПожалуйста, задайте его в настройках аккаунта Telegram.")
            return
        await event.answer()
    else:
        target = event # проверка callback или message
    data = await state.get_data()
    if "username" not in data:
        await state.update_data(username=event.from_user.username)
    data = await state.get_data()
    await event.answer()
    await target.edit_caption(caption=f"""
⭐<b>Покупка звёзд</b>

👤<b>Получатель:</b> @{data['username']}

<b>—Минимум: 50 звёзд</b>
<b>—Максимум(за один заказ): 100 000 звёзд</b>

🔎Выберите количество звёзд для покупки:""",
                                        reply_markup=await kb.choose_amount_stars_keyboard(),
                                        parse_mode="HTML")







@stars_router.message(states.StarsPurchase.username, )
async def input_user_owner_stars(message: Message, state:FSMContext):

    username_own_stars = message.text[1:] if message.text[0] == '@' else message.text

    if len(username_own_stars) >= 4 and \
        all(map(lambda x: ord(x.lower()) in [i for i in range(ord('a'),ord('z')+1)]+[i for i in range(ord('0'),ord('9')+1)]+[ord('_')],username_own_stars)):

        await state.update_data(username=message.text.replace("@", ''))  # ПОМЕНЯТЬ НА СОХРАНЕНИЕ В БД И ОЧИСТКУ ИЗ ОП
        await message.answer_photo(photo=config.visuals.photo_file,
                                   caption=f"⭐<b>Покупка звёзд</b>\n"
                                           f"\n👤<b>Username:</b>  @{username_own_stars}\n"
                                           f"⚠️<b>Проверьте username перед покупкой!</b>",
                                   reply_markup=kb.accept_entered_username_stars_keyboard,
                                   parse_mode="HTML")
    else:
        await message.answer_photo(photo = config.visuals.photo_file,
                                   caption=f"❌<b>Недопустимый username</b>\n"
                                          f"\n🔎<b>Введите username пользователя</b>, которому будем дарить звёзды:\n"
                                          f"—Пример: @{message.from_user.username}",
                                   reply_markup=kb.Input_username_stars_keyboard,
                                   parse_mode="HTML")




@stars_router.callback_query(F.data == "choose_own_amount_stars")
async def own_amount_stars(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_caption(caption=f"""
<b>⭐Покупка звёзд</b>

🔎Введите любое количество звёзд от 50 до 100 000:
— Пример: 1505
""",
                                        reply_markup= kb.Input_amount_stars_keyboard,
                                        parse_mode='HTML')
    await state.set_state(states.StarsPurchase.amount)


@stars_router.callback_query(F.data.startswith('buy_stars'))
async def entered_amount_stars(callback: CallbackQuery, state:FSMContext):

    await callback.answer()
    if callback.data.split("_")[-1] != "back":
        await state.update_data(amount=callback.data.split("_")[-1])
    data = await state.get_data()
    amount = data.get("amount")
    star_price = await get_setting(key="star_course") # цена одной звезды в рублях (тип данных string)

    await callback.message.edit_caption(photo=config.visuals.photo_file,caption=f"""
✨Выбранное количество:<b> {amount} звёзд</b>

👤<b>Получатель:</b> @{data['username']}
    
💰<b>Стоимость:</b> {round(int(data['amount'])*float(star_price),2)} ₽ 
    
👇Выберите метод оплаты👇
            """,
                                            reply_markup=kb.Payment_methods_stars_keyboard,
                                            parse_mode='HTML')



@stars_router.message(states.StarsPurchase.amount,
                      F.text.replace(' ','').isdigit(),
                      lambda m: m.text and m.text.replace(" ", '').isdigit() and 50 <= int(m.text.replace(" ",'')) <= 100_000)

async def entered_amount_stars(message: Message, state:FSMContext):

    amount_stars = message.text.replace(" ", '')
    await state.update_data(amount=amount_stars)
    data = await state.get_data()
    amount = data.get("amount")
    username = message.from_user.username
    if "username" in data:
        username = data["username"]
    star_price = await get_setting(key="star_course")  # цена одной звезды в рублях (тип данных string)



    await message.answer_photo(photo=config.visuals.photo_file,caption=f"""
✨Выбранное количество:<b> {amount} звёзд</b>

👤<b>Получатель:</b> @{username}

💰<b>Стоимость:</b> {round(int(data['amount'])*float(star_price), 2)} ₽

👇Выберите метод оплаты👇
        """,
                                        reply_markup=kb.Payment_methods_stars_keyboard,
                                        parse_mode='HTML')





@stars_router.message(states.StarsPurchase.amount)
async def entered_amount_stars(message:Message):
    await message.answer_photo(photo=config.visuals.photo_file,caption=f"""
⚠️<b>Неправильный ввод</b>⚠️

🔎Введите любое количество звёзд от 50 до 100 000:
— Пример: 1505
""",
                                        reply_markup= kb.Input_amount_stars_keyboard,
                                        parse_mode='HTML')


@stars_router.callback_query(F.data == "sbp_payment_stars")
async def payment_to_sbp_for_purchasing_stars(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    await state.set_state(None)
    await state.update_data(type_payment="sbp")
    data = await state.get_data()
    amount = data.get("amount")
    star_price = await get_setting(key="star_course")  # цена одной звезды в рублях (тип данных string)
    fee = await get_setting(key="cardlink_fee") # комиссия

    await callback.message.edit_caption(caption=f"""
💫Для покупки {amount} звёзд:

<b>1. Нажмите кнопку "Оплатить по СБП"</b>
<b>2. Завершите оплату на открывшейся странице</b>

👤Получатель: @{data['username']}
💵Сумма к оплате: {round(int(data['amount'])*float(star_price), 2)} ₽ 
⚠️Комиссия кассы: {fee}% 

✅ После оплаты бот получит оповещение и автоматически обработает заказ""",
                                        reply_markup=kb.cardlink_payment_keyboard("https://vk.com"),
                                        parse_mode="HTML")





@stars_router.callback_query(F.data == "cryptobot_payment_stars")
async def payment_to_cryptobot_for_purchasing_stars(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()

    await state.set_state(None)
    await state.update_data(type_payment="cryptobot")
    data = await state.get_data()
    amount = data.get("amount")
    star_price = await get_setting(key="star_course")  # цена одной звезды в рублях (тип данных string)
    fee = await get_setting(key="cryptobot_fee")
    amount_fiat = round(int(data["amount"])*float(star_price), 2) # цена
    amount_fiat_with_fee = amount_fiat + (amount_fiat * (int(fee) / 100)) # цена с fiat


    created_invoice = await Cryptobot.create_invoice(amount=amount_fiat_with_fee, description=f"⭐ Покупка {amount} звёзд в StarsCAPITAN")
    pay_url = created_invoice.get("payment_url")
    invoice_id = created_invoice.get("invoice_id")

    data_payment = {"payment_method": "cryptobot", "cost": amount_fiat, "fee": int(fee), "total_cost": amount_fiat_with_fee,
            "sender_id": callback.from_user.id, "product": "stars", "amount": int(data["amount"]), "invoice_id":invoice_id,
                    "recipient_username":data["username"]}

    await add_payment(data=data_payment) # добавляем в БД данные о платеже

    asyncio.create_task(check_payment_loop(invoice_id=invoice_id, user_id=callback.from_user.id,bot=bot,product="stars",username=data["username"],amount_product=data["amount"])) # проверка платежа

    await callback.message.edit_caption(caption=f"""
💫Для покупки {amount} звёзд:

<b>1. Нажмите кнопку "Оплатить Cryptobot"</b>
<b>2. Выберите криптовалюту на открывшейся странице</b>
<b>3. Завершите оплату</b>

💡Номер заказа: {invoice_id}

👤Получатель: @{data['username']}
💵Сумма к оплате: {amount_fiat} ₽ 
⚠️Комиссия кассы: {fee}% 

✅ После оплаты бот получит оповещение и автоматически обработает заказ""",
                                        reply_markup=kb.cryptobot_payment_keyboard(pay_url),
                                        parse_mode="HTML")


@stars_router.callback_query(F.data == "referrer_balance_payment_stars")
async def payment_to_ref_balance_for_purchasing_stars(callback: CallbackQuery, state: FSMContext, bot: Bot):
    user_id =callback.from_user.id
    await callback.answer()

    data = await state.get_data()

    stars_amount = data["amount"]
    star_price = await get_setting(key="star_course")
    amount_fiat = round(int(stars_amount) * float(star_price), 2)

    usdt_to_rub = await get_current_rate("USDT", "RUB")  # находим актуальный курс доллара
    result = await get_user_referrer_balance(user_id=user_id)
    balance = float(result) * usdt_to_rub
    recipient_username = data.get("username")

    if balance >= amount_fiat:

        order_number = uuid.uuid4().hex[:16]
        data_payment = {"payment_method": "referrer_balance", "cost": amount_fiat, "fee": 0,
                        "total_cost": amount_fiat,
                        "sender_id": user_id, "product": "stars", "amount": int(stars_amount),
                        "invoice_id": order_number,
                        "recipient_username": recipient_username, "status":"paid"}

        await add_payment(data=data_payment)  # добавляем в БД данные о платеже
        new_balance = round((balance - amount_fiat) / usdt_to_rub, 4)
        logger.info(f"new balance = {new_balance}")
        await update_referrer_balance(user_id=user_id,new_balance=new_balance)
        await purchase_queue.put(
            {"username": recipient_username, "amount": stars_amount, "product": "stars", "invoice_id": order_number,
             "bot": bot, "admin_message":False})
        await callback.message.edit_caption(caption=f"✅ <b>Оплата прошла успешно.</b>\n\n⭐ Номер заказа: {order_number}\nВозможны задержки до 5 минут.",
                                            parse_mode="HTML")

    else:

        await callback.message.edit_caption(caption=f"❌ <b>Недостаточно средств на балансе.</b>\n\n💵 Приглашайте друзей и зарабатывайте с их покупок.",
                                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                                [InlineKeyboardButton(text="🔙 Назад", callback_data="buy_stars_back")]
                                            ]),
                                            parse_mode="HTML")

@stars_router.callback_query(F.data=="crystalpay_payment_stars")
async def payment_to_crystalpay_for_purchasing_star(callback: CallbackQuery, state: FSMContext,bot: Bot):
    await callback.answer()

    await state.set_state(None)
    await state.update_data(type_payment="crystalpay")
    data = await state.get_data()
    amount = data.get("amount")
    star_price = await get_setting(key="star_course")  # цена одной звезды в рублях (тип данных string)
    fee = await get_setting(key="crystalpay_fee")
    amount_fiat = round(int(amount) * float(star_price), 2)
    recipient_username = data.get("username")

    created_invoice = await Crystalpay.create_invoice(amount=amount_fiat,
                                                     sender_user_id=callback.from_user.id,
                                                    recipient_username=recipient_username,
                                                    product = "stars",
                                                    amount_prod=int(amount))

    invoice_status = created_invoice.get("status")
    invoice_error = created_invoice.get("error")
    logger.info(f"Invoice status: {invoice_status} , invoice error: {invoice_error}")
    if created_invoice.get("status") == 200 and not created_invoice.get("error"):
        pay_url = created_invoice.get("payment_url")
        invoice_id = created_invoice.get("invoice_id")

        data_payment = {"payment_method": "crystalpay", "cost": amount_fiat, "fee": int(fee),
                        "total_cost": amount_fiat,
                        "sender_id": callback.from_user.id, "product": "stars", "amount": int(data["amount"]),
                        "invoice_id": invoice_id,
                        "recipient_username": data["username"]}

        await add_payment(data=data_payment)  # добавляем в БД данные о платеже

        await callback.message.edit_caption(caption=f"""
💫Для покупки {amount} звёзд:
    
<b>1. Нажмите кнопку "Оплатить CrystalPay"</b>
<b>2. Выберите криптовалюту на открывшейся странице</b>
<b>3. Завершите оплату</b>
    
💡Номер заказа: {invoice_id}
    
👤Получатель: @{data['username']}
💵Сумма к оплате: {amount_fiat} ₽ 
    
✅ После оплаты бот получит оповещение и автоматически обработает заказ""",
                                            reply_markup=kb.crystalpay_payment_keyboard(pay_url),
                                            parse_mode="HTML")
    else:
        logger.info(f"Invoice errors: {created_invoice.get('errors')}")
        await callback.message.edit_caption(caption=f"<b>😔 Что-то пошлое не так...</b>\n"
                                                    f"\nПопробуйте создать заказ заново.",
                                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                                [InlineKeyboardButton(text="🏠 На главное меню", callback_data="to_main_menu")]
                                            ]),
                                            parse_mode="HTML")
