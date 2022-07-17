from aiogram import types
from aiogram.dispatcher import FSMContext

from filters.filters import IsManager
from keyboards.default import default_keyboards
from loader import dp
from states.states import SendMessage
from utils.db_api.python_mysql import mysql_connection


@dp.message_handler(IsManager(), commands=['support'], state="*")
async def process_start_command(message: types.Message, state: FSMContext):
    print(message)
    user_id = message.from_user.id
    msg_text = str(message.text)
    conn = mysql_connection()
    c = conn.cursor(buffered=True)
    await state.finish()
    # await SendMessage.first()
    await message.reply("Отправьте, пожалуйста, Ваш вопрос боту @Jarvisrus_support_bot. Последующее общение с "
                        "оператором будет происходить в том же боте, поэтому не блокируйте его и не отключайте "
                        "оповещения")
    c.close()
    conn.close()
