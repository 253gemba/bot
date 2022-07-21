import asyncio
import logging

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from mysql.connector import MySQLConnection  # pip3 install mysql-connector-python

from loader import bot
from utils.db_api.python_mysql import read_db_config


async def get_users_list(c, cities=None):
    if cities is None:
        cities = []
    all_users = []
    for i in cities:
        c.execute("select user_id from users where IF(%s, city_id = %s, 1)",
                  (int(i), i))
        all_users += [x[0] for x in c.fetchall()]
    all_users = list(set(all_users))
    return len(all_users), all_users


async def get_mailing_id(c, conn, user_id):
    c.execute("select * from mailing where user_id = %s and is_sent = 0", (user_id,))
    if c.fetchone() is None:
        c.execute("insert into mailing (user_id) values (%s)", (user_id,))
    conn.commit()
    c.execute("select mail_id from mailing where user_id = %s and is_sent = 0", (user_id,))
    mailing_id = c.fetchone()[0]
    return mailing_id


async def send_mailing(c, mailing_id, user_id, is_admin=0):
    c.execute("select mail_text, mail_addition_type, mail_additional_ident, mail_button_text "
              "from mailing "
              "where mail_id = %s", (mailing_id,))
    mailing_text, mailing_media_type, mailing_media_id, mailing_button_text = c.fetchone()
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
        if mailing_media_id is not None:
            if mailing_media_type == 'gif':
                await bot.send_animation(chat_id=user_id,
                                         caption=mailing_text,
                                         animation=mailing_media_id,
                                         reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_buttons))
            if mailing_media_type == 'video':
                await bot.send_video(chat_id=user_id,
                                     caption=mailing_text,
                                     video=mailing_media_id,
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_buttons))
            if mailing_media_type == 'video_note':
                await bot.send_video_note(chat_id=user_id,
                                          video_note=mailing_media_id,
                                          reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_buttons))
            if mailing_media_type == 'audio':
                await bot.send_audio(chat_id=user_id,
                                     caption=mailing_text,
                                     audio=mailing_media_id,
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_buttons))
            if mailing_media_type == 'voice':
                await bot.send_voice(chat_id=user_id,
                                     caption=mailing_text,
                                     voice=mailing_media_id,
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_buttons))
            if mailing_media_type == 'doc':
                await bot.send_document(chat_id=user_id,
                                        caption=mailing_text,
                                        document=mailing_media_id,
                                        reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_buttons))
            if mailing_media_type == 'photo':
                await bot.send_photo(chat_id=user_id,
                                     caption=mailing_text,
                                     photo=mailing_media_id,
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_buttons))
        else:
            await bot.send_message(user_id,
                                   f'{mailing_text}',
                                   reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_buttons),
                                   disable_web_page_preview=True
                                   )
        return True
    except Exception as e:
        logging.info(e)
        return False


async def go_mailing(mailing_id, users_list=None, cities=None):
    # CONNECT TO DATABASE
    if cities is None:
        cities = []
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    c = conn.cursor(buffered=True)
    c.execute("update mailing set is_sent = 1 where mail_id = %s",
              (mailing_id,))
    conn.commit()
    all_users = await get_users_list(c, cities=cities)

    all_users = all_users[1]

    count_lives = 0
    count_deaths = 0
    if users_list:
        all_users = users_list.split("\n")

    for user_id in all_users:

        is_active = await send_mailing(c, mailing_id, user_id)
        if not is_active:
            c.execute("update users set is_live = 0 where user_id = %s", (user_id,))
            conn.commit()
            count_deaths += 1
        else:
            count_lives += 1
        await asyncio.sleep(0.12)
    # c.execute("delete from mailing where mail_id = %s", (mailing_id,))
    c.execute("update mailing set count_people_all = %s, count_people_get = %s where mail_id = %s",
              (len(all_users), count_lives, mailing_id))
    conn.commit()
    c.close()
    return count_lives, count_deaths
