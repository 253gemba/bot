import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ContentType
from mysql.connector import MySQLConnection

from data.config import ADMINS
from states.states import *
from loader import dp, bot
from keyboards.default.default_keyboards import *
from utils.telegram_functions.telegram_work import get_user_menu, send_message_user, get_message_type
from utils.db_api.python_mysql import read_db_config


@dp.message_handler(lambda message: message.text not in get_buttons_text_from_menu(admin_menu),
                    state=SendMessage.all_states,
                    content_types=ContentType.ANY)
async def communication_with_admin(msg: types.Message, state: FSMContext):
    user_id = msg.from_user.id
    msgtext = msg.text
    # CONNECT TO DATABASE
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    c = conn.cursor(buffered=True)
    now_state = await state.get_state()
    now_state = '' if not now_state else now_state
    state_data = await state.get_data()
    print(now_state, state_data)
    if SendMessage.message_content.state == now_state:
        if result:
            await bot.send_message(user_id,
                                   f'<b>Сообщение доставлено</b> ✔\n\n'
                                   f'💡 <code>Вы можете написать еще одно сообщение или '
                                   f'выполнить любое другое действие</code>',
                                   reply_markup=get_user_menu(c, user_id))
        else:
            await bot.send_message(user_id,
                                   f'🙅‍♂ Сообщение не доставлено, так как пользователь заблокировал бот',
                                   reply_markup=get_user_menu(c, user_id))
    conn.commit()
    c.close()
    conn.close()
