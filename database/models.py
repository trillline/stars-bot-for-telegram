from sqlalchemy import BigInteger, String, func, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from database.base_model import Base

class User(Base):

    __tablename__ = "users"

    # Таблица users содержит информацию о пользователях, которые хотя бы раз нажимали /start в боте.
    # id - уникальный номер в таблице
    # telegram_id - уникальный ID пользователя в Telegram
    # username - актуальный Username пользователя в Telegram (может не быть)
    # referrer_balance - содержит баланс с реферальной программы
    # created_at - дата создания записи о пользователе

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(32), nullable = True)
    chat_id = mapped_column(BigInteger, nullable=False) # id чата с ботом
    referrer_balance: Mapped[float] = mapped_column(Numeric(12,4),default = 0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now()) # дата создания записи

    purchases: Mapped[list["Payment"]] = relationship( # связь один-ко-многим с таблицей payments
        "Payment",
        backref='users'
    )

    referrals: Mapped[list["Referral"]] = relationship( # связь один-ко-многим с таблицей referrals
        "Referral",
        backref="user_referral"
    )

class Payment(Base):
    __tablename__ = "payments"

    # Таблица payments содержит информацию о покупках и платежах.
    # id - уникальный номер в таблице
    # sender_id - ID отправителя в Telegram
    # recipient_username - Username получателя в Telegram
    # invoice_id - номер заказа (генерируется платежными системами)
    # fragment_id - номер операции на fragment.com
    # product - тип заказа (stars или premium)
    # amount - количество единиц товара (кол-во звёзд либо месяцев премиума)
    # payment_method - метод платежа (cryptobot... и т.д)
    # status - статус заказа (pending, paid, expiring)
    # cost - стоимость товара без комиссии
    # fee - комиссия
    # total_cost - стоимость товара с комиссией
    # created_at - дата создания записи с заказом
    # update_at - дата последнего обновления статуса заказа

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sender_id = mapped_column(BigInteger, ForeignKey('users.telegram_id'))
    recipient_username: Mapped[str] = mapped_column(String(32), nullable=True,)
    invoice_id: Mapped[str] = mapped_column(String(32))
    fragment_id: Mapped[str] = mapped_column(String(64), nullable = True)
    product: Mapped[str] = mapped_column(String(32), nullable=True)  # premium | stars
    amount: Mapped[int] = mapped_column(nullable=True)  # кол-во месяцев | кол-во звёзд
    payment_method: Mapped[str] = mapped_column(String(32), nullable = False) # sbp | cryptobot
    status: Mapped[str] = mapped_column(String(32), default = "pending")
    cost: Mapped[float] = mapped_column(Numeric(10,3))
    fee: Mapped[int]
    total_cost: Mapped[float] = mapped_column(Numeric(8,2))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    update_at: Mapped[datetime] = mapped_column(server_default=func.now())


class Setting(Base):
    __tablename__ = "settings"

    # Таблица settings содержит информацию о важных настройках бота,
    # это может быть что угодно так как хранится в парах ключ-значение

    key: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[str]

class Referral(Base):
    __tablename__ = "referrals"

    # Таблица referrals содержит информацию о реферах и рефералах.
    # id - уникальный номер в таблице
    # referrer_id - ID рефера (пригласившего) в Telegram
    # referral_id - ID реферала (приглашенного) в Telegram
    # referral_username - Username реферала в Telegram
    # earned_by_referrer - сумма заработка с этого реферала
    # created_at - дата создания записи
    # updated_at - дата последнего обновления записи

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    referrer_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    referral_id: Mapped[int] = mapped_column(ForeignKey("users.telegram_id"))
    earned_by_referrer: Mapped[float] = mapped_column(Numeric(12,4),default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now())



