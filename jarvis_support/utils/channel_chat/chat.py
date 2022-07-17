import logging

from aiogram.types.message import Message

from keyboards.inline import dynamic
from loader import bot
from utils.telegram_functions.telegram_work import send_message_user
from utils.audio_translater import nanosemantics


async def send_new_message(c, conn, post_id, user_message: Message, is_manager=0, client_message_id=None):
    c.execute("select client_id, chat_message_id, cc_id from answers_posts where post_id = %s", (post_id,))
    client_id, chat_message_id, cc_id = c.fetchone()
    c.execute("select chat_id from channels_and_chats where cc_id = %s", (cc_id,))
    chat_id = c.fetchone()[0]
    translate_text = None
    if user_message.voice:
        try:
            file_data = await user_message.voice.download()
            translate_text = await nanosemantics.translate_audio_to_rus(file_data.name)
        except Exception as e:
            logging.info(e)
    if not is_manager:
        if not client_message_id:
            client_message_id = chat_message_id
        message_to_chat = await user_message.copy_to(chat_id=chat_id,
                                                     reply_to_message_id=client_message_id)
    else:
        if user_message.is_command():
            c.execute("select content_media_type, content_media_id, content_media_text "
                      "from commands "
                      "where command_name = %s", (user_message.text.replace("/", "").split("@")[0],))
            content_media_type, content_media_id, content_media_text = c.fetchone()
            message_to_chat = await send_message_user(client_id, mailing_media_type=content_media_type,
                                                      mailing_media_id=content_media_id,
                                                      mailing_text=content_media_text)
        else:
            message_to_chat = await user_message.copy_to(chat_id=client_id,
                                                         reply_to_message_id=client_message_id)
    if translate_text:
        try:
            print(message_to_chat)
            translate_to_chat = await bot.send_message(chat_id if not is_manager else client_id,
                                                       f"{translate_text}",
                                                       reply_to_message_id=message_to_chat.message_id,
                                                       reply_markup=await dynamic.delete_element(is_delete=0) if is_manager else None)
            c.execute("insert into answers_messages (message_id, post_id, client_id, client_message_id, cc_id, "
                      "manager_message_id) "
                      "values (%s, %s, %s, %s, %s, %s)",
                      (translate_to_chat.message_id if not is_manager else user_message.message_id, post_id, client_id,
                       user_message.message_id if not is_manager else None,
                       cc_id, translate_to_chat.message_id if is_manager else None))
            conn.commit()
        except Exception as e:
            logging.info(e)
    c.execute("insert into answers_messages (message_id, post_id, client_id, client_message_id, cc_id, "
              "manager_message_id) "
              "values (%s, %s, %s, %s, %s, %s)",
              (message_to_chat.message_id if not is_manager else user_message.message_id, post_id, client_id,
               user_message.message_id if not is_manager else None,
               cc_id, message_to_chat.message_id if is_manager else None))
    conn.commit()
