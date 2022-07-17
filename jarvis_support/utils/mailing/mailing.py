import asyncio
import random

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from mysql.connector import MySQLConnection  # pip3 install mysql-connector-python

from keyboards.default import default_keyboards
from keyboards.default.default_buttons import button_segment_all, button_segment_users
from loader import dp, bot
from data.config import ADMINS
from utils.db_api.python_mysql import read_db_config
from utils.telegram_functions.telegram_work import get_user_menu


async def get_users_list(c, department, is_count=0):
    if department == button_segment_users.text:
        c.execute("select user_id from users")
    else:
        c.execute("select user_id from users")
    all_users = c.fetchall()
    users_segment = [x[0] for x in all_users]
    users_segment = list(set(users_segment))
    print(len(users_segment))
    return len(users_segment), users_segment


async def get_mailing_id(c, conn, user_id):
    c.execute("select * from mailing_messages where user_id = %s and is_delay = 0", (user_id,))
    if c.fetchone() is None:
        c.execute("insert into mailing_messages (user_id) values (%s)", (user_id,))
    conn.commit()
    c.execute("select mailing_id from mailing_messages where user_id = %s and is_delay = 0", (user_id,))
    mailing_id = c.fetchone()[0]
    return mailing_id


async def send_mailing(c, mailing_id, user_id, is_admin=0):
    c.execute("select mailing_text, mailing_media_type, mailing_media_id, mailing_button_text, mailing_button_url "
              "from mailing_messages "
              "where mailing_id = %s", (mailing_id,))
    mailing_full_info = c.fetchone()
    mailing_text = mailing_full_info[0]
    mailing_media_type = mailing_full_info[1]
    mailing_media_id = mailing_full_info[2]
    mailing_button_text = mailing_full_info[3]
    mailing_button_url = mailing_full_info[4]
    mailing_button_text = '' if not mailing_button_text else mailing_button_text
    mailing_button_url = 'https://fjfj.ru' if not mailing_button_url else mailing_button_url
    print(user_id, mailing_button_text, mailing_button_url)
    inline_buttons = []
    try:
        for one_row in mailing_button_text.split('\n'):
            inline_buttons.append([])
            for one_button in one_row.split('|'):
                button_text = one_button.split(' - ')[0].strip()
                button_url = one_button.split(' - ')[1].strip()
                inline_buttons[-1].append(InlineKeyboardButton(text=button_text,
                                                               url=button_url))
    except:
        inline_buttons = [[]]
    inline_buttons.append([InlineKeyboardButton(text=f'Удалить из отложки ⭕' if is_admin else '',
                                                callback_data=f'deleteFromDelay_{mailing_id}')])
    inline_buttons.append([InlineKeyboardButton(text=f'Закрыть ✖' if is_admin else '',
                                                callback_data=f'hide')])
    try:
        if len(inline_buttons[0]):
            reply_markup = InlineKeyboardMarkup(inline_keyboard=inline_buttons)
        else:
            reply_markup = default_keyboards.mailing_menu if user_id in ADMINS else get_user_menu(c, user_id)
        if mailing_media_type is not None and mailing_media_type != '':
            if mailing_media_type == 'gif':
                await bot.send_animation(chat_id=user_id,
                                         caption=mailing_text,
                                         animation=mailing_media_id,
                                         reply_markup=reply_markup)
            if mailing_media_type == 'video':
                await bot.send_video(chat_id=user_id,
                                     caption=mailing_text,
                                     video=mailing_media_id,
                                     reply_markup=reply_markup)
            if mailing_media_type == 'video_note':
                await bot.send_video_note(chat_id=user_id,
                                          video_note=mailing_media_id,
                                          reply_markup=reply_markup)
            if mailing_media_type == 'audio':
                await bot.send_audio(chat_id=user_id,
                                     caption=mailing_text,
                                     audio=mailing_media_id,
                                     reply_markup=reply_markup)
            if mailing_media_type == 'voice':
                await bot.send_voice(chat_id=user_id,
                                     caption=mailing_text,
                                     voice=mailing_media_id,
                                     reply_markup=reply_markup)
            if mailing_media_type == 'doc':
                await bot.send_document(chat_id=user_id,
                                        caption=mailing_text,
                                        document=mailing_media_id,
                                        reply_markup=reply_markup)
            if mailing_media_type == 'photo':
                await bot.send_photo(chat_id=user_id,
                                     caption=mailing_text,
                                     photo=mailing_media_id,
                                     reply_markup=reply_markup)
        else:
            await bot.send_message(user_id,
                                   f'{mailing_text}',
                                   reply_markup=reply_markup,
                                   disable_web_page_preview=True
                                   )
        return True
    except Exception as e:
        print(e)
        return False


async def go_mailing(mailing_id, department=button_segment_all.text):
    # CONNECT TO DATABASE
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    c = conn.cursor(buffered=True)
    all_users = await get_users_list(c, department, 0)
    print(all_users)
    all_users = all_users[1]
    print(all_users[0])
    count_lives = 0
    count_deaths = 0
    for user_id in all_users:
        user_id = user_id
        print(user_id)
        is_active = await send_mailing(c, mailing_id, user_id)
        if not is_active:
            c.execute("update users set is_live = 0 where user_id = %s", (user_id,))
            conn.commit()
            count_deaths += 1
        else:
            count_lives += 1
        await asyncio.sleep(0.12)
    c.execute("delete from mailing_messages where mailing_id = %s", (mailing_id,))
    conn.commit()
    c.close()
    return count_lives, count_deaths
