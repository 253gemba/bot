from aiogram import types
from aiogram.dispatcher import FSMContext

from data import config
from keyboards.default import default_keyboards, default_buttons
from loader import dp, bot
from utils.db_api.python_mysql import mysql_connection
from utils.excel.generate_report import do_file_db


@dp.message_handler(
    lambda message: message.text in default_keyboards.get_buttons_text_from_menu(default_keyboards.analytics_menu) and
                    message.from_user.id in config.ADMINS,
    content_types="any", state="*")
async def analytics_menu(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    msg_text = str(message.text)
    conn = mysql_connection()
    c = conn.cursor(buffered=True)
    state_data = await state.get_data()
    state_state = await state.get_state()
    await state.finish()
    if msg_text == default_buttons.button_get_db.text:
        file_name = await do_file_db(c)
        await bot.send_document(user_id,
                                caption='База данных',
                                document=file_name)
    elif msg_text == default_buttons.button_stats.text:
        await bot.send_message(user_id,
                               'Здесь статистика')
    elif msg_text == default_buttons.button_find_users.text:
        await bot.send_message(user_id,
                               'Введите ФИО, ID или номер телефона')
    c.close()
    conn.close()
