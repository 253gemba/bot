from aiogram import types
from aiogram.dispatcher import FSMContext

from filters.filters import IsManager
from keyboards.default import default_keyboards
from keyboards.inline import dynamic_keyboards
from loader import dp
from states.states import SendMessage
from utils.db_api.python_mysql import mysql_connection


@dp.message_handler(IsManager(), commands=['search'], state="*")
async def process_start_command(message: types.Message, state: FSMContext):

    user_id = message.from_user.id
    msg_text = str(message.text)
    conn = mysql_connection()
    c = conn.cursor(buffered=True)
    await state.finish()
    await message.answer("<b>В какой категории Вы бы хотели найти объявление?</b> ⤵",
                         reply_markup=await dynamic_keyboards.get_categories(c, start_query=f'findAdSelectCategory'))
    c.close()
    conn.close()
