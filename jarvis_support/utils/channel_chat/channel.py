import asyncio
import time

from aiogram.types.message import Message
from mysql.connector import MySQLConnection

from loader import bot
from utils.channel_chat.chat import send_new_message
from utils.db_api.python_mysql import read_db_config


async def send_new_post(c, conn, user_id, user_message: Message):
    c.execute("select user_first_name, user_last_name, user_username "
              "from users where user_id = %s", (user_id,))
    user_first_name, user_last_name, user_username = c.fetchone()
    c.execute("select channel_id, chat_id, cc_id from channels_and_chats")
    channel_id, chat_id, cc_id = c.fetchone()
    client_name = f'<a href="tg://user?id={user_id}">' \
                  f'{" ".join([user_first_name, user_last_name if user_last_name else ""])}</a>'
    if user_username:
        client_name += f" (@{user_username})"
    c.execute("select date_format(post_datetime, '%d-%m-%Y %H:%i'), post_id "
              "from answers_posts "
              "where client_id = %s order by post_datetime desc limit 1", (user_id,))
    all_user_posts = c.fetchall()
    all_user_posts = "\n".join([f'<a href="t.me/c/{str(int(channel_id))[3:]}/{post_id}"><b>{post_datetime}</b></a>' for post_datetime, post_id in all_user_posts])
    if all_user_posts:
        all_user_posts = f'<b>📅 Прошлая ветка:</b> {all_user_posts}'
    else:
        all_user_posts = f'☝ Прошлых диалогов не найдено'
    new_post_id = await bot.send_message(channel_id,
                                         f'<b>📧 {client_name}</b>\n\n'
                                         f'{all_user_posts}')
    new_post_id = new_post_id.message_id
    c.execute("insert into answers_posts (post_id, client_id, cc_id) values (%s, %s, %s)",
              (new_post_id, user_id, cc_id))
    conn.commit()
    circle_start = time.time()
    while True:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
        c = conn.cursor(buffered=True)
        print(f'post: {new_post_id}')
        c.execute("select chat_message_id from answers_posts "
                  "where post_id = %s", (new_post_id,))
        chat_message_id = c.fetchone()[0]
        c.execute("select * from answers_posts")
        print(f'test: {c.fetchone()}')
        print(f'chat_message_id: {chat_message_id}')
        if chat_message_id:
            await send_new_message(c, conn, new_post_id, user_message)
            c.close()
            conn.close()
            break
        now_time = time.time()
        if now_time > circle_start + 15:
            c.close()
            conn.close()
            break
        await asyncio.sleep(0.2)
        c.close()
        conn.close()
