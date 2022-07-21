from aiogram import types
from aiogram.dispatcher import FSMContext

from filters.filters import IsManager
from keyboards.default import default_keyboards
from loader import dp
from utils.db_api.python_mysql import mysql_connection


@dp.message_handler(IsManager(), commands=['my_profile'], state="*")
async def process_start_command(message: types.Message, state: FSMContext):

    user_id = message.from_user.id
    msg_text = str(message.text)
    conn = mysql_connection()
    c = conn.cursor(buffered=True)
    await state.finish()
    await message.answer(f'Выберите действие ⤵',
                         reply_markup=default_keyboards.my_profile_menu)
    c.close()
    conn.close()
