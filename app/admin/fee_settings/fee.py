from aiogram import F, Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import load_config
from app.admin.fee_settings import keyboard
from app.admin.states import ChangeFee
from settings import set_setting, get_setting
from logs.logging_bot import logger

fee_settings_router = Router()
config = load_config()

@fee_settings_router.callback_query(F.data == "admin_change_fee", F.from_user.id == config.bot.admin_id)
async def fee_settings(callback: CallbackQuery, bot: Bot):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    cryptobot_fee = await get_setting("cryptobot_fee")
    crystalpay_fee = await get_setting("crystalpay_fee")
    text = f"<b>Окей. Комиссию какого сервиса будем менять?</b>\n\n💎 CryptoBot {cryptobot_fee}% комиссии\n💳 CrystalPay {crystalpay_fee}% комиссии"
    await callback.message.answer(text=text,
                                  reply_markup=keyboard.fee_settings_step1_keyboard(),
                                  parse_mode="HTML")

@fee_settings_router.callback_query(F.data.startswith("change_fee"), F.from_user.id == config.bot.admin_id)
async def set_fee_service(callback: CallbackQuery,state: FSMContext, bot: Bot):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await state.update_data(service=callback.data.split('_')[-1])  # СОХРАНЯЕМ СЕРВИС
    await callback.message.answer(text=f"Введите новый % комиссии.",
                                  reply_markup=keyboard.fee_settings_step2_keyboard())
    await state.set_state(ChangeFee.input) # ЗАДАЁМ СОСТОЯНИЕ

@fee_settings_router.message(ChangeFee.input, F.from_user.id == config.bot.admin_id)
async def change_fee_service(message: Message, state: FSMContext, bot: Bot):

    data = await state.get_data()
    fee = message.text
    service = data["service"]
    if all(list(map(lambda x: ord(x) in [i for i in range(ord('0'), ord('9') + 1)], fee))):
        await set_setting(key=f"{service}_fee", value=fee)
        await state.set_state(None)
        logger.info(f"Комиссия {service} изменена на {fee}%")
        await message.answer(text=f"Комиссия {service} изменена на {fee}%",
                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ОК 🫡", callback_data="admin_panel")]]))
    else:
        logger.warning("Ошибка. Неправильный ввод % комиссии.")
        await message.answer(text=f"Ошибка. Попробуйте ввести % комиссии ещё раз.",
                             reply_markup=keyboard.fee_settings_step2_keyboard())



