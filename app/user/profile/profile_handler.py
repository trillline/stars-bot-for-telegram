from aiogram import Router
from aiogram import F
from aiogram.types import CallbackQuery
import database.requests as rq
import app.user.profile.profile_keyboard as keyboard
from logs.logging_bot import logger
from config import load_config

profile_router = Router()
config = load_config()

@profile_router.callback_query(F.data == "show_profile")
async def show_profile(callback: CallbackQuery):
    await callback.answer()

    profile_data = await rq.get_profile(telegram_id=callback.from_user.id)
    referrer_balance = profile_data.get("referrer_balance")
    total_stars = profile_data.get("total_stars")
    total_premium = profile_data.get("total_premium")
    logger.info(f"\nTHE PROFILE DATA\n{profile_data}\n\n")
    if not profile_data:
        text = (f"🎩 Ваш профиль\n"
                f"\nЧто-то пошло не так...😔\nПопробуйте просмотреть профиль позже.")
    else:
        text = (f"🎩 Ваш профиль\n"
                f"\n👤Ваш ID:<code> {callback.from_user.id}</code>\n"
                f"👥Ваш реферальный баланс: {referrer_balance} ₽\n"
                f"\n🌟Приобретено звёзд: {total_stars if total_stars is not None else 0}\n"
                f"👑Приобретено месяцев премиум-подписки: {total_premium if total_premium is not None else 0 }\n"
                f"\nВы наш {profile_data['id']}-ый пользователь! Спасибо Вам что выбираете нас🫂")

    await callback.message.edit_caption(photo=config.visuals.photo_file, caption=text,
                                        reply_markup=keyboard.profile_keyboard, parse_mode="HTML")
