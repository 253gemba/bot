from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType
from mysql.connector import MySQLConnection

from keyboards.default.default_keyboards import *
from loader import dp, bot
from utils.db_api.python_mysql import read_db_config
from utils.telegram_functions.telegram_work import get_user_menu


@dp.message_handler(lambda message: message.text in get_buttons_text_from_menu(cancel_operation_menu),
                    state="*",
                    content_types=ContentType.ANY)
async def cancel_menu(msg: types.Message, state: FSMContext):
    user_id = msg.from_user.id
    msgtext = msg.text
    # CONNECT TO DATABASE
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    c = conn.cursor(buffered=True)
    now_state = await state.get_state()
    now_state = '' if not now_state else now_state
    print(f'cancel_menu: {user_id}; {msgtext}')
    print(msgtext, button_to_admin.text)
    c.execute("select is_black from users where user_id = %s", (user_id,))
    is_black = c.fetchone()[0]
    await state.finish()
    if is_black:
        await bot.send_message(user_id,
                               f'Ошибка доступа.',
                               reply_markup=types.ReplyKeyboardRemove())
    else:
        if msgtext == button_cancel_operation.text:
            await bot.send_message(user_id,
                                   f'Отменено ✅',
                                   reply_markup=get_user_menu(c, user_id))
    c.close()
    conn.close()
