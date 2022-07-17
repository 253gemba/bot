import asyncio
import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.default import default_keyboards, default_buttons
from loader import dp, bot
from states.states import *
from utils.db_api.python_mysql import mysql_connection
from utils.default_tg.default import get_user_menu


@dp.message_handler(content_types="any", state=Mailing.all_states)
async def mailing_form(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    msg_text = message.text
    conn = mysql_connection()
    c = conn.cursor(buffered=True)
    state_name = await state.get_state()
    state_data = await state.get_data()
    logging.info(f'{msg_text} {user_id}')
    if state_name == Mailing.message_id.state:
        if msg_text == default_buttons.button_mail_start.text:
            c.execute("select user_id from users")
            all_users = [x[0] for x in c.fetchall()]
            await bot.send_message(user_id,
                                   f'<b>Рассылка запущена</b> 📩',
                                   reply_markup=get_user_menu(c, user_id))
            for one_user in all_users:
                try:
                    await bot.copy_message(chat_id=one_user,
                                           from_chat_id=user_id,
                                           message_id=state_data['message_id'])
                except:
                    c.execute("update users set is_live = 0 where user_id = %s", (one_user,))
                    conn.commit()
                await asyncio.sleep(0.05)
            await bot.send_message(user_id,
                                   f'<b>Рассылка прошла успешно</b> 🚀',
                                   reply_markup=get_user_menu(c, user_id))
        else:
            saved_message_id = message.message_id
            await state.update_data(message_id=saved_message_id)
            await bot.copy_message(chat_id=user_id,
                                   from_chat_id=user_id,
                                   message_id=saved_message_id)
            await bot.send_message(user_id,
                                   f'Всё верно? Если да, можете приступать к рассылке. Если нет, отправьте '
                                   f'мне сообщение снова',
                                   reply_markup=default_keyboards.mailing_menu)
    c.close()
    conn.close()
