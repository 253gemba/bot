from aiogram import types
from aiogram.dispatcher import FSMContext

from filters.filters import IsManager
from keyboards.inline import dynamic_keyboards
from loader import dp
from states.states import CreateAd
from utils.db_api.python_mysql import mysql_connection


@dp.message_handler(IsManager(), commands=['post_an_ad'], state="*")
async def process_start_command(message: types.Message, state: FSMContext):
    print(message)
    user_id = message.from_user.id
    msg_text = str(message.text)
    conn = mysql_connection()
    c = conn.cursor(buffered=True)
    await state.finish()
    await CreateAd.first()
    await message.answer("<b>В какой категории Вы бы хотели подать объявление?</b> ⤵",
                         reply_markup=await dynamic_keyboards.get_categories(c))
    c.close()
    conn.close()
