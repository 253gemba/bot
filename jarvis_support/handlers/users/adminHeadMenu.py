import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ContentType
from mysql.connector import MySQLConnection

from keyboards.default import default_keyboards
from keyboards.inline import dynamic
from states.states import *
from loader import dp, bot
from data.config import ADMINS
from keyboards.default.default_keyboards import *
from utils.db_api.python_mysql import read_db_config


@dp.message_handler(lambda message: message.text in get_buttons_text_from_menu(admin_menu),
                    state="*",
                    content_types=ContentType.ANY)
async def admin_head_menu(msg: types.Message, state: FSMContext):
    user_id = msg.from_user.id
    msgtext = msg.text
    # CONNECT TO DATABASE
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    c = conn.cursor(buffered=True)
    now_state = await state.get_state()
    now_state = '' if not now_state else now_state
    logging.info(f'{user_id}; {msgtext}')
    if user_id in ADMINS:
        if msgtext in (button_to_admin.text, button_main_menu.text):
            await bot.send_message(user_id,
                                   f'Выберите кнопку меню ⤵',
                                   reply_markup=admin_menu)

        elif msgtext == button_to_user.text:
            await bot.send_message(user_id,
                                   f'Выберите кнопку меню ⤵',
                                   reply_markup=admin_result)

        elif msgtext == button_payments.text:
            await bot.send_message(user_id,
                                   f'Выберите раздел ⤵',
                                   reply_markup=default_keyboards.payments_menu)

        elif button_new_mailing.text == msgtext:
            await bot.send_message(user_id,
                                   '*Вы попали в меню рассылки *📢\n\n'
                                   'Для возврата нажмите *{0}*\n\n'
                                   'Для отмены какой-либо операции нажмите /start\n\n'
                                   'Используйте *{1}* для предварительного просмотра рассылки, а *{2}* для начала'
                                   ' рассылки\n\n'
                                   'Текст рассылки поддерживает разметку *HTML*, то есть:\n'
                                   '<b>*Жирный*</b>\n'
                                   '<i>_Курсив_</i>\n'
                                   '<pre>`Моноширный`</pre>\n'
                                   '<a href="ссылка-на-сайт">[Обернуть текст в ссылку](test.ru)</a>'.format(
                                       button_main_menu.text, button_mail_preview.text,
                                       button_mail_start.text
                                   ),
                                   parse_mode="markdown",
                                   reply_markup=mailing_menu)

        elif button_commands.text == msgtext:
            inline_kb = await dynamic.get_commands_menu(c)
            await bot.send_message(user_id,
                                   f'Список всех ботов',
                                   reply_markup=inline_kb)
    c.close()
    conn.close()
