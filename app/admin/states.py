from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

class ChangePrice(StatesGroup):
    input_price_star = State()
    input_price_premium = State()

class ChangeFee(StatesGroup):
    service = State()
    input = State()

class Broadcast(StatesGroup):
    wait_text = State()
    wait_photo = State()
    wait_final = State()

class CheckOrder(StatesGroup):
    wait_input_id = State()
    wait_input_username = State()