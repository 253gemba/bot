from aiogram import types
from aiogram.dispatcher.filters import Filter
from mysql.connector import MySQLConnection

from data import config
from loader import dp
from utils.db_api.python_mysql import read_db_config


class IsAnswer(Filter):
    key = 'is_answers'

    async def check(self, message: types.Message):
        if message.chat.id in (config.TECH_CHAT_ID, config.TECH_CHANNEL_ID):
            result = 1
        else:
            result = 0

        return result
