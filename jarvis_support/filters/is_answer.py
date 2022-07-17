from aiogram import types
from aiogram.dispatcher.filters import Filter
from mysql.connector import MySQLConnection

from loader import dp
from utils.db_api.python_mysql import read_db_config


class IsAnswer(Filter):
    key = 'is_answers'

    async def check(self, message: types.Message):
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
        c = conn.cursor(buffered=True)
        c.execute("select count(*) from channels_and_chats where chat_id = %s or channel_id = %s",
                  (message.chat.id, message.chat.id,))
        result = c.fetchone()[0]
        print(f'result: {result}')
        c.close()
        conn.close()
        return result


# class DefineCommand(BoundFilter):
#     key = 'is_custom_command'
#
#     def __init__(self, is_custom_command):
#         self.is_custom_command = is_custom_command
#
#     async def check(self, message: types.Message):
#         db_config = read_db_config()
#         conn = MySQLConnection(**db_config)
#         c = conn.cursor(buffered=True)
#         result_chat = 0
#         result_command = 0
#         if message.is_command():
#             message_text = message.text.replace("/", "")
#             c.execute("select count(*) from channels_and_chats where chat_id = %s or channel_id = %s",
#                       (message.chat.id, message.chat.id,))
#             result = c.fetchone()[0]
#             c.execute("select count(*) from commands where command_name = %s", (message_text,))
#             result_command = c.fetchone()[0]
#             print(f'result: {result}')
#         c.close()
#         conn.close()
#         return result_chat and result_command
