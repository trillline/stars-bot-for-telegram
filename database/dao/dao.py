from database.dao.base import BaseDAO
from database.models import User, Payment, Referral, Setting

class UserDAO(BaseDAO):
    model = User

class PaymentDAO(BaseDAO):
    model = Payment

class ReferralDAO(BaseDAO):
    model = Referral

class SettingDAO(BaseDAO):
    model = Setting
