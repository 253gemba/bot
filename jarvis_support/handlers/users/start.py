import asyncio

from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.utils import deep_linking
from mysql.connector import MySQLConnection

from data.config import ADMINS
from loader import dp, bot
from utils.db_api.python_mysql import read_db_config
from utils.telegram_functions.telegram_work import get_user_menu


@dp.message_handler(CommandStart(), state="*")
async def process_start_command(message: types.Message):
    user_id = message.from_user.id
    msgtext = str(message.text).split('/start')[1].strip()
    print(msgtext)
    # CONNECT TO DATABASE
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    c = conn.cursor(buffered=True)
    c.execute("select count(*) from users where user_id = %s", (user_id,))
    on_database = c.fetchone()[0]
    if not on_database:
        c.execute("insert into users (user_id, date_reg, user_first_name, user_last_name, user_username) "
                  "values (%s, NOW(), %s, %s, %s)",
                  (user_id, message.from_user.first_name, message.from_user.last_name, message.from_user.username))
        conn.commit()
    decode_message = deep_linking.decode_payload(msgtext)
    print(decode_message)
    if 'getbot' in decode_message:
        bot_id = decode_message.split('_')[1]
    else:
        if user_id not in ADMINS:
            await message.reply("👋 <b>Приветствую!</b>\n\n"
                                "Я - бот для <b>тех поддержки</b>",
                                reply=False)
            await asyncio.sleep(1.7)
            await bot.send_chat_action(user_id, 'typing')
            await message.answer(f"📨 Отправь мне сообщение, а я перешлю его администратору бота @Jarvisrus_bot")
        else:
            await message.reply("Добро пожаловать!",
                                reply_markup=get_user_menu(c, user_id),
                                reply=False)
    conn.commit()
    c.close()
    conn.close()
