import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ContentType
from mysql.connector import MySQLConnection

from keyboards.inline import dynamic
from states.states import *
from loader import dp, bot
from keyboards.default.default_keyboards import *
from utils.db_api.python_mysql import read_db_config


@dp.message_handler(lambda message: message.text in get_buttons_text_from_menu(payments_menu),
                    state="*",
                    content_types=ContentType.ANY)
async def func_payment_menu(msg: types.Message, state: FSMContext):
    user_id = msg.from_user.id
    msgtext = msg.text
    # CONNECT TO DATABASE
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    c = conn.cursor(buffered=True)
    now_state = await state.get_state()
    now_state = '' if not now_state else now_state
    logging.info(f'{user_id}; {msgtext}')
    if button_make_payment.text == msgtext:
        await Payments.first()
        await bot.send_message(user_id,
                               f'Напишите сумму платежа')
    if button_personnel.text == msgtext:
        await bot.send_message(user_id,
                               f'Раздел в разработке...')
    c.close()
    conn.close()
