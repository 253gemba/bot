import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart

from data import config
from data.config import ADMINS
from keyboards.default import default_buttons
from loader import dp, bot
from utils.db_api.python_mysql import mysql_connection
from utils.default_tg.default import get_user_menu, decode_link
from utils.steps.define_step import get_future_step


@dp.message_handler(CommandStart(), state="*")
async def process_start_command(message: types.Message, state: FSMContext):

    user_id = message.from_user.id
    msgtext = str(message.text).split('/start')[1].strip()
    conn = mysql_connection()
    c = conn.cursor(buffered=True)
    c.execute("select count(*) from users where user_id = %s", (user_id,))
    on_database = c.fetchone()[0]
    if not on_database:
        c.execute("insert into users (user_id, tg_first_name, tg_last_name, tg_username) "
                  "values (%s, %s, %s, %s)",
                  (user_id, message.from_user.first_name, message.from_user.last_name, message.from_user.username))
        conn.commit()
    if msgtext:
        decode_msg = await decode_link(msgtext)

        if not on_database:
            if 'utm' in decode_msg:
                utm_id = decode_msg.split("_")[1]
                c.execute("select bonus from utm where utm_id = %s", (utm_id,))
                bonus = c.fetchone()[0]
                c.execute("update users set utm_id = %s, bonus_value = %s where user_id = %s",
                          (utm_id, bonus, user_id))
                conn.commit()
    if user_id not in ADMINS:
        await bot.send_message(user_id,
                               f'👋 <b>Приветствую!</b>\n\n'
                               f'Меня зовут <b>Джарвис</b>. Я - бот по поиску и размещению объявлений')
        await asyncio.sleep(2)
        c.execute("select count(*) from users where user_id = %s and city_id is not NULL",
                  (user_id,))
        await bot.send_chat_action(user_id, "typing")
        if c.fetchone()[0]:
            await message.answer(f"<b>Краткий гайд по использованию бота</b> 👇\n\n"
                                 f"<b>/{config.COMMANDS[0][0]}</b> - найти объявление\n"
                                 f"<b>/{config.COMMANDS[1][0]}</b> - подать объявления\n"
                                 f"<b>/{config.COMMANDS[2][0]}</b> - настроить оповещения\n"
                                 f"<b>/{config.COMMANDS[3][0]}</b> - изменить город, баланс\n"
                                 f"<b>/{config.COMMANDS[4][0]}</b> - задать вопрос",
                                 reply_markup=get_user_menu(c, user_id))
        else:
            await message.answer("<b>Давайте познакомимся?</b>\n\n"
                                 "Для начала знакомства мне потребуется <b>регион поиска/размещения</b> "
                                 "объявлений. Его можно выбрать вручную или определить автоматически\n\n"
                                 "<b>Какой вариант выберем?</b>",
                                 reply_markup=get_user_menu(c, user_id))
    else:
        await message.reply("Добро пожаловать!",
                            reply_markup=get_user_menu(c, user_id),
                            reply=False)
    conn.commit()
    c.close()
    conn.close()
