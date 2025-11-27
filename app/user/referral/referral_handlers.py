from aiogram import F, Router
from aiogram.types import CallbackQuery
from database.requests import get_refsys_info, get_referrals
from data_redis import RAMdata
import app.user.referral.referral_keyboard as keyboard
from config import load_config

referral_router = Router()
config = load_config()

@referral_router.callback_query(F.data == "show_referral_system")
async def show_referral_system(callback: CallbackQuery):
    await callback.answer()

    info = await get_refsys_info(telegram_id=callback.from_user.id)

    if not info:
        text = (f"👥<b>Реферальная система</b>\n"
                f"\nЧто-то пошло не так...😔\nПопробуйте просмотреть профиль позже.")
    else:
        referral_link = f"https://t.me/{config.bot.username}?start={callback.from_user.id}"
        text = (f"👥<b>Реферальная программа</b>\n"
                f"\nПриглашайте друзей по вашей уникальной ссылке и получайте прибыль с их покупок!\n"
                f"\n📊<b>Ваша статистика:</b>\n"
                f"— Количество рефералов: {info['amount_ref']}\n"
                f"— Ваш общий доход: {info['total_cash']} ₽\n"
                f"— Доступно для вывода: {info['available_cash']} ₽\n"
                f"\n🔗<b>Ваша реферальная ссылка: </b><code>{referral_link}</code>\n"
                f'\n🔎<b>Подробности программы:</b>\nНажми на кнопку "Подробности программы" ниже чтобы получить больше информации.')

    await callback.message.edit_caption(photo=config.visuals.photo_file, caption=text,
                                        reply_markup=keyboard.menu, parse_mode="HTML")


@referral_router.callback_query(F.data == "refsys_information")
async def get_information_about_referral_system(callback: CallbackQuery):
    await callback.answer()

    text = (f"🎖️<b>Условия программы:</b>\n"
            f"Вы получаете 30% от чистой прибыли, которую приносит ваш реферал.\n"
            f"\n💳<b>Куда они зачисляются?</b>\n"
            f"На ваш реферальный баланс внутри бота.\n"
            f"\n💵<b>Как я могу их потратить?</b>\n"
            f"Вы можете приобрести звёзды или премиум-подписку в нашем боте за средства реферального баланса.")

    await callback.message.edit_caption(photo=config.visuals.photo_file, caption=text
                                        ,reply_markup=keyboard.info, parse_mode="HTML")

@referral_router.callback_query(F.data == "check_referrals")
async def check_referral(callback: CallbackQuery):
    await callback.answer()

    referrals = await get_referrals(telegram_id=callback.from_user.id) # List[Dict]

    text=(f"👥<b> Список рефералов</b>"
          f"\n\nСтруктура списка:\n<i>username : заработано</i>\n")
    for ref in referrals:
        text += f"\n@{ref['referral_username']} : {round(float(ref['earned_by_referrer']),2)} $"

    await callback.message.edit_caption(photo=config.visuals.photo_file, caption=text,
                                        reply_markup=keyboard.info, parse_mode="HTML")


