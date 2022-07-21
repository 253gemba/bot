from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp
from states.states import GetReferral
from utils.db_api.python_mysql import mysql_connection
from utils.referral.referrals import attach_referral, is_valid


@dp.message_handler(state=GetReferral.answer)
async def process_message(message: types.Message, state: FSMContext):
    conn = mysql_connection()
    c = conn.cursor(buffered=True)
    referral_link = message.text
    if len(referral_link) < 20 or len(referral_link) > 20:
        await message.answer('Неверный формат ссылки')
    else:
        flag = is_valid(referral_link)
        if flag:
            current_user = message.from_id
            attach_referral(c, conn, current_user, referral_link)
            await message.answer(f'Ссылка {referral_link} прикреплена')
        else:
            await message.answer('Ссылка не валидна')
    await state.finish()
