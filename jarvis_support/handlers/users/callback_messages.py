import os
import subprocess
from urllib.request import urlopen

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from mysql.connector import MySQLConnection

from data import config
from keyboards.inline.dynamic import edit_command_menu
from utils.db_api.python_mysql import read_db_config
from keyboards.default import default_keyboards
from keyboards.default.default_buttons import button_cancel_operation
from keyboards.inline import dynamic
from loader import dp, bot
from states.states import *
from utils.fast_answers.commands import get_command_info
from utils.payments.yookassa_func import create_payment
from utils.telegram_functions.telegram_work import get_user_menu
from utils.users.get_user_info import get_info_user


@dp.callback_query_handler(state="*")
async def process_callback_messages(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    query_id = callback_query.id
    # CONNECT TO DATABASE
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    c = conn.cursor(buffered=True)
    try:
        message_id = callback_query.message.message_id
    except:
        message_id = callback_query.inline_message_id
    query_data = callback_query.data
    message = callback_query.message
    print(f'CallbackQuery: {user_id} -> {query_data}')
    start_data = query_data.split('_')[0]
    close_kb = [
        [InlineKeyboardButton(text=f'Закрыть ✖',
                              callback_data=f'hide')]
    ]
    try:
        one_param = query_data.split('_')[1]
    except:
        one_param = None
    try:
        two_param = query_data.split('_')[2]
    except:
        two_param = None
    try:
        three_param = query_data.split('_')[3]
    except:
        three_param = None
    try:
        four_param = query_data.split('_')[4]
    except:
        four_param = None
    if 'hide' == start_data:
        await state.finish()
        await bot.delete_message(user_id, message_id)

    elif 'deleteMediaFromMailing' == start_data:
        c.execute("update mailing_messages set mailing_media_type = NULL, mailing_media_id = '' "
                  "where is_delay = 0 and user_id = %s",
                  (user_id,))
        conn.commit()
        await bot.send_message(user_id,
                               f'Медиа очищены')

    elif 'deleteTextFromMailing' == start_data:
        c.execute("update mailing_messages set mailing_text = NULL "
                  "where is_delay = 0 and user_id = %s",
                  (user_id,))
        conn.commit()
        await bot.send_message(user_id,
                               f'Текст очищен')

    elif 'deleteButtonFromMailing' == start_data:
        c.execute("update mailing_messages set mailing_button_text = NULL, mailing_button_url = NULL "
                  "where is_delay = 0 and user_id = %s",
                  (user_id,))
        conn.commit()
        await bot.send_message(user_id,
                               f'Кнопки очищены')

    elif 'deleteFromDelay' == start_data:
        c.execute("delete from mailing_messages where mailing_id = %s",
                  (one_param,))
        conn.commit()
        await bot.send_message(user_id,
                               f'Отложка очищена')

    elif 'deletePayMethod' == start_data:
        if two_param:
            c.execute("delete from users_payment_methods where id = %s",
                      (one_param,))
            conn.commit()
            await bot.answer_callback_query(user_id,
                                            f'Удалено 👌',
                                            show_alert=True)
            await message.delete()
        else:
            await bot.send_message(user_id,
                                   f'Вы уверены, что хотите удалить метод оплаты?',
                                   reply_markup=await dynamic.delete_element(query_data))

    elif 'hideKeyboard' == start_data:
        await bot.edit_message_reply_markup(chat_id=user_id,
                                            message_id=message_id,
                                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                                [InlineKeyboardButton(text=f'✅',
                                                                      callback_data=f' ')]
                                            ]))

    elif 'seeInfo' == start_data:
        find_user_id = one_param
        return_text, inline_kb = await get_info_user(c, find_user_id)
        await bot.send_message(user_id,
                               f'{return_text}',
                               reply_markup=inline_kb)

    elif 'doPayment' == start_data:
        payment_type = one_param
        bot_id = two_param
        c.execute("select server_payment, service_payment from client_bots where bot_id = %s", (bot_id,))
        server_payment, service_payment = c.fetchone()
        payment_value = server_payment if 'server' in payment_type else service_payment
        if not three_param:
            inline_kb = InlineKeyboardMarkup(row_width=1)
            inline_kb.insert(InlineKeyboardButton(text=f'месяц - {payment_value}₽',
                                                  callback_data=f'{query_data}_{1}'))
            inline_kb.insert(InlineKeyboardButton(text=f'3 месяца - {int(payment_value * 3)}₽',
                                                  callback_data=f'{query_data}_{3}'))
            inline_kb.insert(InlineKeyboardButton(text=f'6 месяцев - {int(payment_value * 0.9 * 6)}₽ (-10%)',
                                                  callback_data=f'{query_data}_{6}'))
            inline_kb.insert(InlineKeyboardButton(
                text=f'12 месяцев - {int(payment_value * 0.85 * 12)}₽ (-15%)',
                callback_data=f'{query_data}_{12}'))
            inline_kb.insert(InlineKeyboardButton(text='↩ Назад',
                                                  callback_data=f'botInfo_{bot_id}_1'))
            await bot.send_message(chat_id=user_id,
                                   text=f'Выберите количество месяцев для оплаты',
                                   reply_markup=inline_kb)
        else:
            months = int(three_param)
            if months in (1, 3):
                payment_value = payment_value * months
            elif months == 6:
                payment_value = int(payment_value * 0.9 * months)
            elif months == 12:
                payment_value = int(payment_value * 0.85 * months)
            payment = await create_payment(payment_value)
            print(payment)
            system_id = payment["id"]
            c.execute("insert into payments (system_id, bot_id, user_id, payment_type, months, payment_system) "
                      "values (%s, %s, %s, %s, %s, 2)",
                      (system_id, bot_id, user_id, payment_type, months))
            conn.commit()
            payment_id = c.lastrowid
            payment_type_ru = 'сервер' if 'server' in payment_type else 'обслуживание'
            await bot.send_message(user_id,
                                   f'⏱ Время зачисления средств обычно составляет <b>до 5 минут</b>, но может быть '
                                   f'изменено в связи с техническими моментами\n\n'
                                   f'<b>Для оплаты {payment_value}₽ за {payment_type_ru}, нажмите кнопку ниже</b> ⤵',
                                   reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                       [InlineKeyboardButton(text=f'Оплатить',
                                                             url=f'{payment["confirmation"]["confirmation_url"]}')]
                                   ]))

    elif 'commandsPage' == start_data:
        page = one_param
        await message.edit_reply_markup(await dynamic.get_commands_menu(c, page))

    elif 'editCommand' == start_data:
        command_id = one_param
        await get_command_info(c, command_id, user_id,
                               inline_kb=await edit_command_menu(c, command_id))

    elif 'addCommand' == start_data:
        await CreateCommand.command_name.set()
        await bot.send_message(user_id,
                               f'Напишите <b>название команды</b>. К примеру: /send_hello '
                               f'(без пробелов и иных знаков, кроме нижнего подчеркивания и латинского алфавита)',
                               reply_markup=default_keyboards.cancel_operation_menu)

    elif 'editBlackUser' == start_data:
        find_user_id = one_param
        c.execute("update users set is_black = abs(is_black - 1) where user_id = %s", (find_user_id,))
        conn.commit()
        return_text, inline_kb = await get_info_user(c, find_user_id)
        await bot.edit_message_text(chat_id=user_id,
                                    message_id=message_id,
                                    text=return_text,
                                    reply_markup=inline_kb)

    elif 'editCommandAnswer' == start_data:
        command_id = one_param
        await CreateCommand.command_content.set()
        await state.update_data(command_id=command_id)
        await bot.send_message(user_id,
                               f'<b>Текущее значение ⤵</b>')
        await get_command_info(c, command_id, user_id, with_content=1)
        await bot.send_message(user_id,
                               f'Отправьте новое значение',
                               reply_markup=default_keyboards.cancel_operation_menu)

    elif 'editCommandDescription' == start_data:
        command_id = one_param
        await CreateCommand.command_description.set()
        await state.update_data(command_id=command_id)
        await bot.send_message(user_id,
                               f'Отправьте новое значение',
                               reply_markup=default_keyboards.cancel_operation_menu)

    elif 'editCommandName' == start_data:
        command_id = one_param
        await CreateCommand.command_name.set()
        await state.update_data(command_id=command_id)
        await bot.send_message(user_id,
                               f'Введите новое значение',
                               reply_markup=default_keyboards.cancel_operation_menu)

    elif 'editNameDB' == start_data:
        bot_id = one_param
        await CreateBot.source_database.set()
        await state.update_data(bot_id=bot_id)
        await bot.send_message(user_id,
                               f'Введите новое значение',
                               reply_markup=default_keyboards.cancel_operation_menu)

    await bot.answer_callback_query(query_id)
    c.close()
    conn.close()
