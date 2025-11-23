from sqlalchemy import BigInteger, String, func, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from database.base_model import Base



class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(32), nullable = True)
    chat_id = mapped_column(BigInteger, nullable=False) # id чата с ботом
    referrer_balance: Mapped[float] = mapped_column(Numeric(12,4),default = 0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now()) # дата создания записи

    purchases: Mapped[list["Payment"]] = relationship(
        "Payment",
        backref='users'
    )

    referrals: Mapped[list["Referral"]] = relationship(
        "Referral",
        backref="user_referral"
    )


class Payment(Base):
    __tablename__ = "payments"

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

    key: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[str]

class Referral(Base):
    __tablename__ = "referrals"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    referrer_id: Mapped[int] = mapped_column(ForeignKey("users.telegram_id"))
    referral_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    referral_username: Mapped[str] = mapped_column(String(32))
    earned_by_referrer: Mapped[float] = mapped_column(Numeric(12,4),default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now())



