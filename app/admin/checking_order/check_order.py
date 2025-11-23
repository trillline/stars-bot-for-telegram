from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Router, F, Bot
from app.admin.states import CheckOrder
from database.requests import get_payment_info_by_id, get_username_by_id
#from fragment.fragment_api import check_order

checkOrder_router = Router()



@checkOrder_router.callback_query(F.data == "admin_check_order")
async def checking_id_order(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await callback.message.answer(text="🆔 Введите ID заказа:",
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                      [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_panel")]
                                  ]))
    await state.set_state(CheckOrder.wait_input_id)

@checkOrder_router.message(CheckOrder.wait_input_id)
async def info_about_order_by_id(message: Message, state: FSMContext):
    id = message.text
    data = await get_payment_info_by_id(invoice_id=id)
    if data:
        username = await get_username_by_id(user_id=data.get("sender_id"))
        date = str(data.get("created_at"))
        text = (f"Заказ №{id}\n"
                f"👤Отправитель: @{username} (ID:{data.get('sender_id')})\n"
                f"👤Получатель: @{data.get('recipient_username')}\n"
                f"🎁Товар: {'Звёзды' if data.get('product') == 'stars' else 'Премиум'}\n"
                f"🤏Кол-во: {data.get('amount')} {'мес.' if data.get('product') == 'premium' else ''}\n"
                f"🏦Платёжная система: {data.get('payment_method')}\n"
                f"⌛Статус оплаты: {'Оплачено ✅' if data.get('status') == 'paid' else 'Не оплачено ❌'}\n"
                f"💵 Стоимость: {data.get('cost')} ₽\n"
                f"🕑Время создания заказа: {date[:date.rfind('.')]}\n")
      #  if data.get("fragment_id") is not None:
      #      order = await check_order(data.get("fragment_id"))
      #      if order.get("status") == 200 and order.get("success"):
      #          text += (f"💡Fragment ID операции: {data.get('fragment_id')}\n"
      #                   f"#️⃣Fragment Ref_id: {order.get('ref_id')}")
      #  else:
      #      text += "💡Fragment ID операции: Нет"

        await message.answer(text=text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👌 OK", callback_data="admin_check_order")]
        ]))
    else:
        await message.answer(text=f"Заказ №{id} не найден.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👌 OK", callback_data="admin_check_order")]
        ]))

