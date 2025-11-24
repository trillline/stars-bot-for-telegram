
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func

from config import load_config
from database.db_settings import connection
from database.models import User, Referral, Payment
from database.dao.dao import UserDAO, ReferralDAO, PaymentDAO
from logs.logging_bot import logger
from datetime import datetime, timezone
from config import load_config
from payments.cryptobot_payments import get_current_rate

@connection
async def if_username_changed_update(session: AsyncSession, tg_id:int, username:str):
    stmt = select(User.username).filter_by(telegram_id=tg_id)
    result = await session.execute(stmt)
    db_username = result.scalar_one()

    if db_username != username:
        stmt = (
            update(User)
            .where(User.telegram_id == telegram_id)  # type: ignore
            .values(username=username)
        )
        await session.execute(stmt)
        await session.commit()

@connection
async def initialize_user(session:AsyncSession, telegram_id, username, **data_user):
    # получаем данные о пользователе (для проверки существования в БД)
    stmt = select(User).filter_by(telegram_id=telegram_id)
    result_user_exists = await session.execute(stmt) # получаем данные о пользователе из БД
    try:
        user =  result_user_exists.scalar_one_or_none() # возвращает объект с одной записью или None, иначе ошибка
    except Exception:
        logger.error(f"The user {telegram_id} is doubled in DB")
        return
    # если пользователь отсутствует
    if user is None:
        await UserDAO.add(session,telegram_id=telegram_id,username=username,**data_user)

@connection
async def check_referral_exists(session:AsyncSession, user_id):

    stmt = select(User).filter_by(telegram_id=user_id)
    result = await session.execute(stmt)
    user = result.one_or_none()
    if user is None:
        return False
    else:
        return True

@connection
async def get_total_stars_by_user(session: AsyncSession, telegram_id: int):
    stmt_total_stars = select(func.sum(Payment.amount)).filter_by(sender_id=telegram_id, product="stars", status="paid")
    result_star = await session.execute(stmt_total_stars)
    return result_star.scalar()

@connection
async def get_total_premium_month_by_user(session: AsyncSession, telegram_id: int):
    stmt_month_premium = select(func.sum(Payment.amount)).filter_by(sender_id=telegram_id, product="premium",
                                                                    status="paid")
    result_premium = await session.execute(stmt_month_premium)
    return result_premium.scalar()

@connection
async def get_profile(session:AsyncSession, telegram_id: int):
    result_dict = {}
    try:
        # Загружаем профиль. Нужно получить поле реферальный баланс, количество купленных звёзд
        # а также количество купленных месяцев премиум подписки. Всё это хранится в таблице users
        result_dict["total_stars"] = await get_total_stars_by_user(telegram_id=telegram_id)

        result_dict["total_premium"] = await get_total_premium_month_by_user(telegram_id=telegram_id)

        user_data = select(User.id, User.referrer_balance).filter_by(telegram_id = telegram_id)
        result_user = await session.execute(user_data)
        user = result_user.one_or_none()
        usdt_to_rub = await get_current_rate("USDT", "RUB")
        result_dict["id"], result_dict["referrer_balance"] = user.id, round(float(user.referrer_balance) * usdt_to_rub,2)


        return result_dict

    except (Exception, StopIteration):
        logger.error("PROFILE SELECTION ERROR")
        return {}

@connection
async def get_refsys_info(session: AsyncSession, telegram_id):
    result_dict = {}
    try:
        stmt_amount = select(func.count(Referral.referral_id)).filter_by(referrer_id = telegram_id)
        result_amount = await session.execute(stmt_amount)
        result_dict["amount_ref"] = result_amount.scalar_one()

        stmt_cash = select(User.referrer_balance).filter_by(telegram_id=telegram_id)
        result_cash = await session.execute(stmt_cash)
        usdt_to_rub = await get_current_rate("USDT", "RUB")
        cash_usdt = result_cash.scalar_one()
        if cash_usdt:
            result_dict["available_cash"] = round( float(cash_usdt) * usdt_to_rub , 2)
        else:
            result_dict["available_cash"] = 0.00
        stmt_total_cash = select(func.sum(Referral.earned_by_referrer)).filter_by(referrer_id=telegram_id)
        result_total_cash = await session.execute(stmt_total_cash)
        total_cash_usdt = result_total_cash.scalar_one()
        if total_cash_usdt:
            result_dict["total_cash"] = round(float(total_cash_usdt) * usdt_to_rub , 2)
        else:
            result_dict["total_cash"] = 0.00

        return result_dict

    except Exception:
        logger.error("REFERRAL SELECTION ERROR")

@connection
async def get_referrals(session:AsyncSession, telegram_id):

    try:
        stmt = select(Referral.referral_username, Referral.earned_by_referrer).filter_by(referrer_id=telegram_id)
        result = await session.execute(stmt)
        rows = result.all()

        referrals = [
        ]

        for row in rows:
            data = {"referral_username":row.referral_username, "earned_by_referrer":row.earned_by_referrer}
            referrals.append(data)

        return referrals
    except Exception:
        logger.error("GET REFERRALS ERROR")


@connection
async def add_referral(session: AsyncSession, referrer_id, referral_id, referral_username):

    stmt = select(Referral.id).filter_by(referrer_id=referrer_id, referral_id=referral_id)
    result = await session.execute(stmt)

    if result.scalar_one_or_none() is None:
        await ReferralDAO.add(session, referrer_id=referrer_id, referral_id=referral_id,
                          referral_username=referral_username,updated_at=datetime.utcnow())

@connection
async def get_common_total_stars(session: AsyncSession):

    stmt = select(func.sum(Payment.amount)).filter_by(status="paid", product="stars")
    result = await session.execute(stmt)
    common_stars = result.scalar_one_or_none()
    if common_stars:
        return common_stars
    else:
        return 0

@connection
async def get_all_chat_id(session: AsyncSession):
    config = load_config()
    admin_id = config.bot.admin_id
    stmt = select(User.chat_id)
    result = await session.execute(stmt)
    chat_id_db = result.scalars().all()
    chats = [z  for z in chat_id_db if z != admin_id]

    return chats

@connection
async def add_payment(session: AsyncSession, data):
    await PaymentDAO.add(session, **data)

@connection
async def update_status_payment(session: AsyncSession, invoice_id: str, status: str):
    stmt = update(Payment).filter_by(invoice_id=invoice_id).values(status=status, update_at = datetime.utcnow())
    await session.execute(stmt)
    await session.commit()

@connection
async def give_referrer_reward(session: AsyncSession, referral_id: int, amount: float):
    referrer = await get_referrer(referral_id=referral_id) # ищем реферов
    if referrer is not None:
        usdt_to_rub = await get_current_rate("USDT", "RUB") # находим актуальный курс доллара
        referrer_amount = (amount / usdt_to_rub) * 0.01 # получка рефера
        logger.info(f"Текущий курс: {usdt_to_rub}")
        logger.info(f"Рефер заработает: {referrer_amount}")

        # ищем сколько рефер получил за это реферала уже
        stmt_earned_ref = select(Referral.earned_by_referrer).filter_by(referrer_id=referrer, referral_id=referral_id)
        earned_ref = await session.execute(stmt_earned_ref)
        earned = earned_ref.scalar()

        # обновляем заработок рефера с этого реферала (поле earned_by_referrer)
        stmt_update_ref = update(Referral).filter_by(referrer_id=referrer, referral_id=referral_id).values(
            earned_by_referrer=float(earned) + referrer_amount)
        await session.execute(stmt_update_ref)

        # ищем текущий баланс реферра и за все время
        stmt_user_balance = select(User.referrer_balance).filter_by(telegram_id=referrer)
        res_user_balance = await session.execute(stmt_user_balance)
        user_balance = res_user_balance.scalar()

        # обновляем их значения: то что было + получка
        stmt_update_user_balance = update(User).filter_by(telegram_id=referrer).values(
            referrer_balance=float(user_balance) + referrer_amount)
        await session.execute(stmt_update_user_balance)

        await session.commit()



# получить рефера конкретного реферала
@connection
async def get_referrer(session: AsyncSession, referral_id: int):
    stmt = select(Referral.referrer_id).filter_by(referral_id=referral_id)
    result = await session.execute(stmt)
    referrer = result.scalar()
    return referrer

@connection
async def update_fragment_id(session: AsyncSession,invoice_id,fragment_id):
    stmt = update(Payment).filter_by(invoice_id=invoice_id).values(fragment_id=fragment_id)
    await session.execute(stmt)
    await session.commit()


@connection
async def get_payment_info_by_id(session: AsyncSession, invoice_id):
    stmt = select(Payment).filter_by(invoice_id = invoice_id)
    result = await session.execute(stmt)
    payment = result.scalar_one_or_none()
    if payment:
        info_payment = {"payment_method":payment.payment_method, "status":payment.status, "cost":payment.total_cost, "created_at":payment.created_at,
                    "product":payment.product, "amount":payment.amount, "fragment_id":payment.fragment_id, "sender_id":payment.sender_id, "recipient_username":payment.recipient_username}
        return info_payment
    else:
        return None

@connection
async def get_username_by_id(session: AsyncSession, user_id):
    stmt = select(User.username).filter_by(telegram_id=user_id)
    result = await session.execute(stmt)
    username = result.scalar()
    return username

@connection
async def get_user_referrer_balance(session: AsyncSession, user_id):
    stmt = select(User.referrer_balance).filter_by(telegram_id=user_id)
    result = await session.execute(stmt)
    referrer_balance = result.scalar()
    return referrer_balance

@connection
async def update_referrer_balance(session: AsyncSession, user_id, new_balance):
    stmt = update(User).filter_by(telegram_id=user_id).values(referrer_balance=new_balance)
    await session.execute(stmt)
    await session.commit()