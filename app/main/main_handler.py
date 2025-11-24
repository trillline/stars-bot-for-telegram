from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

import app.main.main_keyboard as kb
import database.requests as rq
from config import load_config
from database.requests import check_referral_exists
from logs.logging_bot import logger

config = load_config()


main_router = Router()




@main_router.callback_query(F.data=="to_main_menu")
@main_router.message(CommandStart())
async def start_message(event: Message | CallbackQuery, state: FSMContext):
    if isinstance(event, CallbackQuery):
        event_bot = event.message
        await event_bot.delete()
    else:
        event_bot = event
        start_sms = event.text.split(" ")
        logger.info(f"Received the start message: {start_sms}")
        if len(start_sms) > 1:
            referrer_id = int(start_sms[1])
            user_exists = await check_referral_exists(user_id=event.from_user.id)
            if referrer_id != event.from_user.id and not user_exists:
                await rq.add_referral(referrer_id=referrer_id, referral_id=event.from_user.id, referral_username=event.from_user.username)
        await rq.initialize_user(telegram_id=event.from_user.id, username=event.from_user.username, chat_id=event.chat.id)

    common_total_stars = await rq.get_common_total_stars()


    await state.clear()
    await event_bot.answer_photo(caption=f"""
🤗Привет, {event.from_user.full_name}!

<i>Здесь вы можете быстро приобрести Telegram Stars и Telegram Premium за рубли или криптовалюту</i>

⭐️При помощи нашего сервиса купили {common_total_stars} звёзд""",
                               reply_markup=kb.get_main_menu_keyboard(event.from_user.id),
                                 photo=config.visuals.photo_file,
                                 parse_mode="HTML")




