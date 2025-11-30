from aiogram import F, Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import load_config
import app.admin.price_settings.keyboard as keyboard
import app.admin.states as st
from settings import set_setting
from logs.logging_bot import logger

price_settings_router = Router()

config = load_config()

@price_settings_router.callback_query(F.data == "admin_change_price",F.from_user.id == config.bot.admin_id)
async def price_settings(callback:CallbackQuery, bot:Bot):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await callback.message.answer(text="<b>Окей. Какие цены будем менять?</b>",
                                  reply_markup=keyboard.price_settings_step1_keyboard(),
                                  parse_mode="HTML")


@price_settings_router.callback_query(F.data == "admin_change_star_price", F.from_user.id == config.bot.admin_id)
async def set_price_star(callback: CallbackQuery,state:FSMContext, bot: Bot):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await callback.message.answer(text="<b>Укажите цену за 1 звезду, отделяя целую часть точкой</b>\nПример: 1.33",
                                  reply_markup=keyboard.price_settings_step2_keyboard(),
                                  parse_mode="HTML")
    await state.set_state(st.ChangePrice.input_price_star)

@price_settings_router.message(st.ChangePrice.input_price_star, F.from_user.id == config.bot.admin_id)
async def check_received_price_stars(message: Message, state: FSMContext):

    price = message.text
    if all(list(map(lambda x: ord(x) in ([i for i in range(ord('0'), ord('9') + 1)] + [ord('.')]), price)))\
            and price.count('.') <= 1 and (price.find('.')==1 or price.find('.')==-1) and len(price) != 2:

        await set_setting(key="star_course", value=price)
        await state.set_state(None)
        logger.info("Цена 1 звезды изменена.")
        await message.answer(text=f"Цена изменена.\n\n⭐ Цена за 1 звезду = {price} ₽",
                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="OK 👌", callback_data="admin_panel")]]))
    else:
        logger.warning("Ошибка. Неправильный ввод для изменения цены 1 звезды")
        await message.answer(text="Ошибка. Попробуйте ввести цену ещё раз.",
                             reply_markup=keyboard.price_settings_step3_keyboard())


@price_settings_router.callback_query(F.data.startswith("admin_change_premium_price"), F.from_user.id == config.bot.admin_id )
async def set_price_premium(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    month_number = int(callback.data.split("_")[-1])
    await callback.message.answer(text=f"<b>Укажите цену за {month_number} мес. премиум-подписки.</b>",
                                  reply_markup=keyboard.price_settings_step2_keyboard(),
                                  parse_mode="HTML")
    await state.update_data(input_price_premium= month_number)
    await state.set_state(st.ChangePrice.input_price_premium)

@price_settings_router.message(st.ChangePrice.input_price_premium, F.from_user.id == config.bot.admin_id)
async def check_received_price_premium(message: Message, state: FSMContext):

    price = message.text
    if all(list(map(lambda x: ord(x) in ([i for i in range(ord('0'), ord('9') + 1)] + [ord('.')]), price)))\
        and price.count('.') <= 1:

        data = await state.get_data()
        month = data.get('input_price_premium')
        await set_setting(key=f"price_premium_{month}", value=price)
        await state.set_state(None)
        logger.info(f"Цена премиум-подписки на {month} месяца изменена.")
        await message.answer(text=f"Цена изменена.\n\n👑 Цена премиум-подписки на {month} мес. = {price} ₽",
                             reply_markup=InlineKeyboardMarkup(
                                 inline_keyboard=[[InlineKeyboardButton(text="OK 👌", callback_data="admin_panel")]]))
    else:
        logger.warning("Ошибка. Неправильный ввод для изменения цены премиум-подписки.")
        await message.answer(text="Ошибка. Попробуйте ввести цену ещё раз.",
                                 reply_markup=keyboard.price_settings_step3_keyboard())
