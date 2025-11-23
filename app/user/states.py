from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

class Product(StatesGroup):
    purchased = State() # куплено (да или нет)
    type_purchase = State()  # тип покупки
    type_payment = State()
    active_invoice = State()

class StarsPurchase(StatesGroup):
    username = State() # юзерка получателя звёзд/премиума
    amount = State()  # количество звёзд или количество месяцев Premium подписки

class PremiumPurchase(StatesGroup):
    username = State()
    month = State()

class BotUsername(StatesGroup):
    username = State()

class GlobalTechnicalMode(StatesGroup):
    technical_mode = State()

async def clear_previous_state(previous_state: str, state: FSMContext):
    data = await state.get_data()
    data.pop(previous_state,None)
    await state.set_data(data)