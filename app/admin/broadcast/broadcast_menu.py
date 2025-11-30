from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Router, F, Bot
from data_redis import RAMdata
import app.admin.broadcast.keyboard as kb
from app.admin.states import Broadcast
from database.requests import get_all_chat_id
from logs.logging_bot import logger
from aiogram.exceptions import TelegramForbiddenError

broadcast_router = Router()

async def get_broadcast_data():
    text = await RAMdata.get("broadcast_text")
    photo = await RAMdata.get("broadcast_photo")
    button = await RAMdata.get("broadcast_button")
    return {"broadcast_text":text, "broadcast_photo":photo, "broadcast_button":button}


@broadcast_router.callback_query(F.data == "admin_broadcast")
async def broadcast_text(callback: CallbackQuery,state: FSMContext, bot: Bot):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await RAMdata.delete("broadcast_text", "broadcast_photo", "broadcast_button")
    logger.info("Переход в рассылку в админ-панели")
    await callback.message.answer(text='<b>Отправь мне текст для рассылки или нажми на кнопку "Нет текста"</b>\n\n',
                          reply_markup=kb.broadcast_text(),
                                  parse_mode="HTML")
    await state.set_state(Broadcast.wait_text)


@broadcast_router.callback_query(F.data == "no_text_broadcast")
@broadcast_router.message(Broadcast.wait_text)
async def broadcast_photo(event: CallbackQuery | Message, state:FSMContext, bot: Bot):
    await RAMdata.delete("broadcast_photo")
    if isinstance(event, Message):
        target = event
        text = target.text
        await RAMdata.set("broadcast_text", text)
    else:
        target = event.message
        await bot.delete_message(target.chat.id, target.message_id)
    await target.answer(text="<b>Отправь мне фото для рассылки или нажми на кнопку 'Нет фото'</b>",
                        reply_markup=kb.broadcast_photo(),
                        parse_mode="HTML")
    await state.set_state(Broadcast.wait_photo)

@broadcast_router.callback_query(F.data == "no_photo_broadcast")
@broadcast_router.message(Broadcast.wait_photo, F.photo)
async def broadcast_button(event: CallbackQuery | Message, state:FSMContext, bot: Bot):
    if isinstance(event, Message):
        target = event
        photo_id = target.photo[-1].file_id
        await RAMdata.set("broadcast_photo", photo_id)
    else:
        target = event.message
        await bot.delete_message(target.chat.id, target.message_id)
    await target.answer(text="<b>Выбери какая кнопка будет прикреплена к рассылке или нажми на кнопку 'Нет кнопки'</b>",
                        reply_markup=kb.broadcast_button(),
                        parse_mode="HTML")
    await state.set_state(None)


@broadcast_router.callback_query(F.data.startswith("broadcast_button"))
@broadcast_router.message(Broadcast.wait_final, F.text.lower() == "назад")
async def complete_broadcast(event: Message | CallbackQuery, state: FSMContext, bot: Bot):
    if isinstance(event, CallbackQuery):
        target = event.message
        button = event.data.split("_")[-1]
        await RAMdata.set("broadcast_button", button)
        await bot.delete_message(target.chat.id, target.message_id)
    else:
        target = event
    await state.set_state(None)
    logger.info("Рассылка создана!")
    await target.answer(text="<b>Создание рассылки завершено!</b>\n\n"
                            'Для отправки напишите "отправить"\n'
                             'Для возвращения назад напишите "назад"',
                          reply_markup= kb.broadcast_complete(),
                          parse_mode= "HTML")

@broadcast_router.callback_query(F.data == "broadcast_checking")
async def checking_broadcast(callback: CallbackQuery,state:FSMContext, bot: Bot):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    data = await get_broadcast_data()
    if data["broadcast_photo"] is not None:
        await callback.message.answer_photo(caption=data["broadcast_text"],
                                            reply_markup=kb.get_button(data["broadcast_button"], "fake"),
                                            photo=data["broadcast_photo"],
                                            parse_mode = "HTML")
        await state.set_state(Broadcast.wait_final)
    elif data["broadcast_text"] is not None:
        await callback.message.answer(text=data["broadcast_text"], reply_markup=kb.get_button(data["broadcast_button"], "fake"), parse_mode="HTML")
        await state.set_state(Broadcast.wait_final)
    else:
        await callback.message.answer(text="Нет никакой основы для рассылки. Фото и текст отсутствуют.",
                                      reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                          [InlineKeyboardButton(text="Начать заново", callback_data="admin_broadcast")]
                                      ]))

@broadcast_router.message(Broadcast.wait_final, F.text.lower() == "отправить")
async def send_broadcast(message: Message, bot: Bot):
    chats_id = await get_all_chat_id()
    data = await get_broadcast_data()

    if data["broadcast_photo"] is not None:
        for chat_id in chats_id:
            logger.info(f"chat id = {chat_id}")
            try:
                await bot.send_photo(chat_id=chat_id,photo=data["broadcast_photo"],caption=data["broadcast_text"],reply_markup=kb.get_button(data["broadcast_button"]), parse_mode="HTML")
            except TelegramForbiddenError:
                logger.error(f"Последний ID заблокировал бота")
    else:
        for chat_id in chats_id:
            logger.info(f"chat id = {chat_id}")
            try:
                await bot.send_message(chat_id=chat_id, text=data["broadcast_text"], reply_markup=kb.get_button(data["broadcast_button"]), parse_mode="HTML")
            except TelegramForbiddenError:
                logger.error(f"Последний ID заблокировал бота")
    logger.info("Рассылка отправлена!")
    await message.answer(text="✅ Рассылка завершена",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                             [InlineKeyboardButton(text="🏠 Вернуться к главному меню", callback_data="admin_panel")]
                         ]))
