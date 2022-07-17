from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ContentType
from mysql.connector import MySQLConnection

from states.states import *
from loader import dp, bot
from keyboards.default.default_keyboards import *
from utils.mailing.mailing import send_mailing, get_users_list, go_mailing
from utils.db_api.python_mysql import read_db_config


@dp.message_handler(lambda message: message.text in get_buttons_text_from_menu(mailing_menu),
                    state="*",
                    content_types=ContentType.ANY)
async def mail_head_menu(msg: types.Message, state: FSMContext):
    user_id = msg.from_user.id
    msgtext = msg.text
    # CONNECT TO DATABASE
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    c = conn.cursor(buffered=True)
    now_state = await state.get_state()
    now_state = '' if not now_state else now_state
    print(f'mail_head_menu: {user_id}; {msgtext}')
    if msgtext in (button_to_admin.text, button_main_menu.text):
        await bot.send_message(user_id,
                               f'Выберите кнопку меню ⤵',
                               reply_markup=admin_menu)

    elif msgtext == button_mail_text.text:
        await Mailing.wait_mail_text.set()
        await bot.send_message(user_id,
                               f'Пришлите текст рассылки',
                               reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                   [InlineKeyboardButton(text=f'Удалить текст ⭕',
                                                         callback_data=f'deleteTextFromMailing')]
                               ])
                               )

    elif msgtext in (button_mail_media.text,):
        await Mailing.wait_mail_media.set()
        await bot.send_message(user_id, 'Отправьте медиа файл ответным сообщением',
                               reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                   [InlineKeyboardButton(text=f'Удалить медиа ⭕',
                                                         callback_data=f'deleteMediaFromMailing')]
                               ]))

    elif msgtext == button_mail_see_delayed.text:
        c.execute("select mailing_id, is_delay, mailing_media_type from mailing_messages "
                  "where is_delay <> 0 and user_id = %s",
                  (user_id,))
        all_mailings_delayed = c.fetchall()
        inline_kb = []
        for one_mailing_info in all_mailings_delayed:
            mailing_id = one_mailing_info[0]
            is_delay = one_mailing_info[1]
            mailing_media_type = one_mailing_info[2]
            inline_kb.append([InlineKeyboardButton(text=f'#{mailing_id}; '
                                                        f'media: {mailing_media_type if mailing_media_type is not None else "без медиа"}',
                                                   callback_data=f'seeMailing_{mailing_id}')])
        await bot.send_message(user_id,
                               f'Выберите рассылку, чтобы посмотреть или удалить ее из очереди',
                               reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_kb))

    elif msgtext == button_mail_preview.text:
        await state.finish()
        c.execute("select mailing_id from mailing_messages "
                  "where is_delay = 0 and user_id = %s",
                  (user_id,))
        try:
            mailing_id = c.fetchone()[0]
            is_true = await send_mailing(c, mailing_id, user_id)
            if not is_true:
                raise
        except Exception as e:
            print(e)
            await bot.send_message(user_id,
                                   f'Произошла какая-то ошибка. Попробуйте загрузить текст, медиа или кнопку '
                                   f'заново и повторить попытку. Также убедитесь, что в ссылке кнопки '
                                   f'(если она есть) присутствует протокол (https:// или http://)')

    elif button_mail_start.text == msgtext:
        await bot.send_message(user_id,
                               f'Выберите количество аудитории',
                               reply_markup=mail_segment_menu)

    elif msgtext in get_buttons_text_from_menu(mail_segment_menu):
        c.execute("select mailing_id from mailing_messages where user_id = %s and is_delay = 0", (user_id,))
        mailing_id = c.fetchone()[0]
        await state.finish()
        count_users = await get_users_list(c, msgtext, 1)
        count_users = count_users[0]
        await bot.send_message(user_id,
                               f'Начинаю рассылку...\n\n'
                               f'⏱ Приблизительное время, которое будет затрачено на рассылку: '
                               f'{count_users * 0.15}с\n\n'
                               f'Кол-во юзеров: {count_users}',
                               reply_markup=admin_menu)
        result_mailing = await go_mailing(mailing_id, msgtext)
        await bot.send_message(user_id,
                               f'<b>✔ Результаты рассылки</b>\n\n'
                               f'<b>Живые:</b> {result_mailing[0]}\n'
                               f'<b>Заблокировали бот:</b> {result_mailing[1]}')

    elif button_mail_do_delay.text == msgtext:
        c.execute("select mailing_id from mailing_messages "
                  "where user_id = %s and is_delay = %s",
                  (user_id, 0))
        mailing_id = c.fetchone()
        if mailing_id is None:
            await bot.send_message(user_id,
                                   f'Откладывать нечего! Сначала создайте сообщение для рассылки')
        else:
            await Mailing.delay_mail.set()
            await state.update_data(mailing_id=mailing_id[0])
            await bot.send_message(user_id,
                                   f'<b>Напишите дату и время, в которое должно отправиться сообщение</b>\n\n'
                                   f'Формат: <code>ДД ММ ГГГГ чч мм</code>')

    elif button_mail_button.text == msgtext:
        await Mailing.mail_button_text.set()
        await bot.send_message(user_id,
                               f'Напишите кнопки в формате:\n\n'
                               f'Кнопка - ссылка | Кнопка - ссылка\n'
                               f'Кнопка - ссылка и т.д.',
                               reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                   [InlineKeyboardButton(text=f'Удалить кнопки ⭕',
                                                         callback_data=f'deleteButtonFromMailing')]
                               ]))
    c.close()
    conn.close()