from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from mysql.connector import MySQLConnection

from loader import dp, bot
from states.states import *
from utils.db_api.python_mysql import read_db_config


@dp.message_handler(state=FindUser.states, content_types=types.ContentType.ANY)
async def process_find_user(message: types.Message, state: FSMContext):
    print(message)
    user_id = message.from_user.id
    msg_text = str(message.text)
    # CONNECT TO DATABASE
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    c = conn.cursor(buffered=True)
    now_state = await state.get_state()
    now_data = await state.get_data()
    print(f'process_find_user: {user_id}; {msg_text}')
    if now_state == FindUser.user_id.state:
        await state.finish()
        if set(msg_text) < set('0123456789'):
            c.execute("select user_id from users where user_id like %s",
                      (f'%{msg_text}%',))
            all_users = c.fetchall()
            all_find_id = [x[0] for x in all_users]
        elif '@' in msg_text:
            username = str(msg_text).split('@')[1]
            c.execute("select user_id from users where username like %s",
                      (f'%{username}%',))
            all_users = c.fetchall()
            all_find_id = [x[0] for x in all_users]
        else:
            c.execute("select user_id from users where full_name like %s or first_name like %s",
                      (f'%{msg_text}%', f'%{msg_text}%',))
            all_users = c.fetchall()
            all_find_id = [x[0] for x in all_users]
        try:
            all_users_kb = []
            for one_find_id in all_find_id:
                c.execute("select user_id, full_name, username from users where user_id = %s",
                          (one_find_id,))
                all_info = c.fetchone()
                chat_id_find = all_info[0]
                first_name = all_info[1]
                username = all_info[2]
                if len(all_users_kb) < 15:
                    try:
                        all_users_kb.append([InlineKeyboardButton(text=f'ID: {chat_id_find} '
                                                                       f'{first_name} @{username}',
                                                                  callback_data=f'seeInfo_{chat_id_find}')])
                    except:
                        pass
            await bot.send_message(user_id,
                                   f'Выберите пользователя из списка',
                                   reply_markup=InlineKeyboardMarkup(inline_keyboard=all_users_kb))
        except Exception as e:
            print(e)
            await bot.send_message(user_id,
                                   f'Пользователь не найден :(')
    c.close()
    conn.close()
