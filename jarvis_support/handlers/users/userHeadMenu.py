from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ContentType
from mysql.connector import MySQLConnection

from keyboards.inline import dynamic
from states.states import *
from loader import dp, bot
from data.config import ADMINS
from keyboards.default.default_buttons import *
from keyboards.default.default_keyboards import *
from utils.db_api.python_mysql import read_db_config


@dp.message_handler(lambda message: message.text in get_buttons_text_from_menu(user_menu) or
                                    message.text in get_buttons_text_from_menu(client_menu),
                    state="*",
                    content_types=ContentType.ANY)
async def user_head_menu(msg: types.Message, state: FSMContext):
    user_id = msg.from_user.id
    msgtext = msg.text
    # CONNECT TO DATABASE
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    c = conn.cursor(buffered=True)
    now_state = await state.get_state()
    now_state = '' if not now_state else now_state
    print(f'user_head_menu: {user_id}; {msgtext}')
    print(msgtext, button_to_admin.text)
    c.execute("select is_black from users where user_id = %s", (user_id,))
    is_black = c.fetchone()[0]
    await state.finish()
    if is_black:
        await bot.send_message(user_id,
                               f'Ошибка доступа.')
    else:
        if msgtext == button_cases.text:
            await bot.send_message(user_id,
                                   f'<b>👏 Список всех кейсов:</b> https://t.me/otziv_tgdev/28\n\n'
                                   f'<b>☝ Отзывы:</b> https://t.me/otziv_tgdev/18',
                                   disable_web_page_preview=True)
            await bot.copy_message(chat_id=user_id,
                                   from_chat_id=940108284,
                                   message_id=182,
                                   caption=f'А еще у нас есть презентация некоторых популярных ботов и '
                                           f'<a href="https://www.youtube.com/watch?v=4qGOBTSAZtY">видео на ютуб</a> '
                                           f'с небольшой демонстрацией 😎')
        elif msgtext == button_do_account_bot.text:
            await SendMessage.first()
            await bot.send_message(user_id,
                                   f'✅ Для удобства расчета мы составили <b>чек-лист</b> вопросов:\n\n'
                                   f'1. Какой у Вас бизнес? Чем занимается? (если бот для бизнеса)\n'
                                   f'2. Опишите цели, которых необходимо достичь при помощи бота 🏆\n'
                                   f'3. Какие бизнес-процессы должен облегчить бот? (если бот для бизнеса)\n'
                                   f'4. Есть ли у Вас ссылки на похожие проекты? 🔗\n'
                                   f'5. Почему пользователи будут использовать этот бот?\n'
                                   f'6. Опишите подробно основные функции бота (рассылка, аналитика, ответы на '
                                   f'вопросы и т.д.)\n'
                                   f'7. Планируется ли мультиязычность в боте (несколько языков)? 🇬🇧\n\n'
                                   f'<b>Пишите все ответы прямо здесь. Я всё отправлю на расчет. Можете еще '
                                   f'следующим сообщением картинку отправить. Или голосовое. Как угодно :)</b>')
        elif msgtext == button_my_bots.text:
            return_text, return_kb = await get_bot_list(c, user_id)
            await bot.send_message(user_id,
                                   f'{return_text}',
                                   reply_markup=return_kb)
        elif msgtext == button_lk.text:
            inline_kb = await dynamic.auto_payments(c, user_id, 0)
            await bot.send_message(user_id,
                                   f'В этом разделе Вы можете управлять платежами и картами. '
                                   f'Карту можно удалить нажатием на кнопку с данными карты',
                                   reply_markup=inline_kb)
        elif msgtext == button_question.text:
            await SendMessage.first()
            await bot.send_message(user_id,
                                   f'Напишите Ваш вопрос. Мы постараемся ответить на него в самое ближайшее время')
    c.close()
    conn.close()
