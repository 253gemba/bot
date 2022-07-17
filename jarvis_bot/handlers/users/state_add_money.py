import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.default import default_keyboards
from loader import dp
from states.states import *
from utils.db_api.python_mysql import mysql_connection
from utils.external_systems.yookassa_payments import create_payment


@dp.message_handler(content_types="any", state=AddMoney.all_states)
async def add_money(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    msg_text = message.text
    conn = mysql_connection()
    c = conn.cursor(buffered=True)
    state_name = await state.get_state()
    state_data = await state.get_data()
    logging.info(f'{user_id} {msg_text}')
    if msg_text.isdigit():
        pay_link = await create_payment(payment_value=msg_text, user_id=user_id)
        print(pay_link)
        c.execute("insert into payments (user_id, payment_amount, system_id) values (%s, %s, %s)",
                  (user_id, msg_text, pay_link['id']))
        conn.commit()
        await state.finish()
        await message.answer(f"⏱ <b>Средства будут зачислены в течение 5 минут после оплаты\n\n"
                             f"👇 Ссылка на оплату</b>\n\n"
                             f"{pay_link['confirmation']['confirmation_url']}",
                             reply_markup=default_keyboards.ReplyKeyboardRemove())
    else:
        await message.answer("⚠ Введите сумму пополнения цифрами. Например: 2000")
    c.close()
    conn.close()
