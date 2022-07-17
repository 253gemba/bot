import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

from filters.filters import IsAdmin
from keyboards.default import default_keyboards, default_buttons
from keyboards.inline import dynamic_keyboards
from loader import dp, bot
from states.states import CreateAd, Mailing
from utils.db_api.python_mysql import mysql_connection


@dp.message_handler(IsAdmin(),
                    lambda message: message.text in default_keyboards.get_buttons_text_from_menu(
                        default_keyboards.admin_menu),
                    content_types="any", state="*")
async def admin_menu(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    msg_text = str(message.text)
    conn = mysql_connection()
    c = conn.cursor(buffered=True)
    logging.info(f'{user_id} {msg_text}')
    state_data = await state.get_data()
    state_state = await state.get_state()
    await state.finish()
    if msg_text == default_buttons.button_new_mailing.text:
        await Mailing.first()
        await bot.send_message(user_id,
                               f'<b>Вы попали в меню рассылки </b>📢\n\n'
                               f'Для возврата нажмите <b>{default_buttons.button_main_menu.text}</b>\n\n'
                               f'Жирный шрифт, курсив, внутренние ссылки - все поддерживается\n\n'
                               f'<b>Отправьте сообщение, которое хотите разослать ⤵</b>',
                               reply_markup=default_keyboards.go_to_head_menu)
    elif msg_text == default_buttons.button_personnel.text:
        await bot.send_message(user_id,
                               f'Выберите раздел ⤵',
                               reply_markup=default_keyboards.personnel_menu)
    elif msg_text == default_buttons.button_analytics.text:
        await bot.send_message(user_id,
                               f'Выберите раздел ⤵',
                               reply_markup=default_keyboards.analytics_menu)
    c.close()
    conn.close()
