from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType
from mysql.connector import MySQLConnection

from filters.is_answer import IsAnswer
from keyboards.default import default_keyboards
from loader import dp
from utils.channel_chat import chat, channel
from utils.db_api.python_mysql import read_db_config
from utils.default_tg.default import get_user_menu


@dp.message_handler(content_types="any", state="*")
async def test(message: types.Message, state: FSMContext):
    # CONNECT TO DATABASE

    user_id = message.from_user.id
    db_config = read_db_config()
    conn = MySQLConnection(**db_config)
    c = conn.cursor(buffered=True)
    c.execute("select count(*) from users where user_id = %s and city_id is NULL", (user_id,))
    if c.fetchone()[0]:
        await message.answer("<b>Давайте познакомимся?</b>\n\n"
                             "Для начала знакомства мне потребуется <b>регион поиска/размещения</b> "
                             "объявлений. Его можно выбрать вручную или определить автоматически\n\n"
                             "<b>Какой вариант выберем?</b>",
                             reply_markup=get_user_menu(c, user_id))
    c.close()
    conn.close()


# @dp.message_handler(IsAnswer(),
#                     content_types=ContentType.ANY)
# async def get_messages_from_chat(msg: types.Message, state: FSMContext):
#     # CONNECT TO DATABASE
#     print(msg)
#     db_config = read_db_config()
#     conn = MySQLConnection(**db_config)
#     c = conn.cursor(buffered=True)
#     now_state = await state.get_state()
#     now_state = '' if not now_state else now_state
#     state_data = await state.get_data()
#     if msg.reply_to_message:
#         reply_chat_id = msg.reply_to_message.chat.id
#         reply_user_id = msg.reply_to_message.from_user.id
#         print(f'reply_user_id: {reply_user_id}')
#         print(f'reply_chat_id: {reply_chat_id}')
#         if reply_user_id == 777000:
#             c.execute("select post_id from answers_posts where chat_message_id = %s",
#                       (msg.reply_to_message.message_id,))
#             post_id = c.fetchone()[0]
#             c.execute("select client_id, post_id, client_message_id from answers_messages "
#                       "where post_id = %s",
#                       (post_id,))
#             client_id, post_id, client_message_id = c.fetchone()
#             client_message_id = None
#         else:
#             c.execute("select client_id, post_id, client_message_id from answers_messages "
#                       "where message_id = %s",
#                       (msg.reply_to_message.message_id,))
#             client_id, post_id, client_message_id = c.fetchone()
#         await chat.send_new_message(c, conn, post_id, msg, is_manager=1, client_message_id=client_message_id)
#     else:
#         if msg.forward_from_message_id:
#             chat_message_id = msg.message_id
#             c.execute("select chat_message_id from answers_posts where post_id = %s", (msg.forward_from_message_id,))
#             if not c.fetchone()[0]:
#                 c.execute("update answers_posts set chat_message_id = %s where post_id = %s",
#                           (chat_message_id, msg.forward_from_message_id))
#             conn.commit()
#     c.close()
#     conn.close()
#
#
# @dp.message_handler(state="*",
#                     content_types=ContentType.ANY)
# async def any_messages(msg: types.Message, state: FSMContext):
#     msgtext = msg.text
#     user_id = msg.from_user.id
#     # CONNECT TO DATABASE
#     dbconfig = read_db_config()
#     conn = MySQLConnection(**dbconfig)
#     c = conn.cursor(buffered=True)
#     now_state = await state.get_state()
#     now_state = '' if not now_state else now_state
#     state_data = await state.get_data()
#     print(msg)
#     try:
#         c.execute("update users set tg_first_name = %s, tg_username = %s, tg_last_name = %s "
#                   "where user_id = %s",
#                   (msg.from_user.first_name, msg.from_user.username, msg.from_user.last_name, user_id))
#         conn.commit()
#     except:
#         pass
#
#     # if user_id not in ADMINS:
#     c.execute("select post_id, post_datetime, chat_message_id "
#               "from answers_posts "
#               "where client_id = %s and date_add(post_datetime, interval 1 hour) > NOW()"
#               "order by post_datetime desc", (user_id,))
#     user_answers = c.fetchone()
#     if user_answers:
#         post_id, post_datetime, chat_message_id = user_answers
#         if msg.reply_to_message:
#             c.execute("select message_id from answers_messages where manager_message_id = %s",
#                       (msg.reply_to_message.message_id,))
#             client_message_id = c.fetchone()[0]
#         else:
#             client_message_id = None
#         try:
#             await chat.send_new_message(c, conn, post_id, msg, client_message_id=client_message_id)
#         except:
#             await channel.send_new_post(c, conn, user_id, msg)
#     else:
#         await channel.send_new_post(c, conn, user_id, msg)
#     await msg.answer("📧 Ваше сообщение отправлено администратору. На ответ может потребоваться некоторое время",
#                      reply_markup=default_keyboards.ReplyKeyboardRemove())
#     c.close()
#     conn.close()
