import datetime
import time

from aiogram import types
from aiogram.dispatcher import FSMContext
from mysql.connector import MySQLConnection

from keyboards.default.default_keyboards import mailing_menu
from utils.db_api.python_mysql import read_db_config
from utils.mailing.mailing import get_mailing_id

from states.states import *
from loader import dp, bot
from utils.telegram_functions.telegram_work import get_message_type


@dp.message_handler(state=Mailing.states, content_types=types.ContentType.ANY)
async def mailing(message: types.Message, state: FSMContext):
    # CONNECT TO DATABASE
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    c = conn.cursor(buffered=True)
    user_id, msg_text = message.from_user.id, message.text
    now_state = await state.get_state()
    state_data = await state.get_data()
    # обработка состояний
    if now_state == Mailing.wait_mail_text.state:
        await state.finish()
        mailing_id = await get_mailing_id(c, conn, user_id)
        print(mailing_id)
        c.execute("update mailing_messages set mailing_text = %s where mailing_id = %s",
                  (message.html_text, mailing_id))
        await bot.send_message(user_id,
                               f'Текст сохранен! ✅',
                               reply_markup=mailing_menu)

    elif now_state == Mailing.wait_mail_media.state:
        message_type = await get_message_type(message)
        mailing_media_type, mailing_media_id = message_type
        if mailing_media_id is None:
            await bot.send_message(user_id,
                                   f'Формат данного сообщения не поддерживается, отправьте другое')
        else:
            mailing_id = await get_mailing_id(c, conn, user_id)
            c.execute("update mailing_messages set mailing_media_type = %s, mailing_media_id = %s "
                      "where mailing_id = %s", (mailing_media_type, mailing_media_id, mailing_id))
            await state.finish()
            await bot.send_message(user_id,
                                   f'Медиа сообщение сохранено! ✅',
                                   reply_markup=mailing_menu)

    elif Mailing.delay_mail.state == now_state:
        mailing_id = state_data['mailing_id']
        if len(msg_text.split(' ')) == 5 and set(msg_text) < set('0123456789 '):
            msgtext = msg_text.split()
            day_text = int(msgtext[0])
            month_text = int(msgtext[1])
            year_text = int(msgtext[2])
            hour_time = int(msgtext[3])
            minute_time = (msgtext[4])
            data_format = f'{day_text}-{month_text}-{year_text} {hour_time}:{minute_time}'
            dt = datetime.datetime.strptime(data_format, '%d-%m-%Y %H:%M')
            is_delay = dt.timestamp()
            if is_delay > time.time():
                c.execute("update mailing_messages set is_delay = %s where mailing_id = %s",
                          (is_delay, mailing_id))
                await bot.send_message(user_id,
                                       f'✅ <b>Отлично, отложенное сообщение будет разослано</b> {data_format}')
                await state.finish()
            else:
                await bot.send_message(user_id,
                                       f'Отложенное сообщение не может быть отправлено раньше текущей даты. '
                                       f'Укажите дату и время позже, чем дата и время сейчас')
        else:
            bot.send_message(user_id, 'Неверный формат. Повторите попытку\n\n'
                                      'ДЕНЬ МЕСЯЦ ГОД ЧАСЫ МИНУТЫ')

    elif now_state == Mailing.mail_button_text.state:
        mailing_id = await get_mailing_id(c, conn, user_id)
        c.execute("update mailing_messages set mailing_button_text = %s "
                  "where mailing_id = %s", (msg_text, mailing_id))
        await state.finish()
        print(f'sbros')
        await bot.send_message(user_id,
                               f'Готово ✅')

    elif now_state == Mailing.mail_button_link.state:
        mailing_id = await get_mailing_id(c, conn, user_id)
        c.execute("update mailing_messages set mailing_button_url = %s "
                  "where mailing_id = %s",
                  (msg_text, mailing_id))
        await state.finish()
        await bot.send_message(user_id,
                               f'✅ <b>Кнопка добавлена</b>')
    conn.commit()
    c.close()
    conn.close()
