from aiogram import types
from aiogram.dispatcher.filters import Filter

from data.config import ADMINS
from utils.db_api.python_mysql import mysql_connection


class IsAdmin(Filter):
    key = 'is_admin'

    async def check(self, m: types.Message):
        user_id = m.from_user.id
        is_admin = user_id in ADMINS
        return is_admin


class IsUser(Filter):
    key = 'is_user'

    async def check(self, m: types.Message):
        user_id = m.from_user.id
        conn = mysql_connection()
        cur = conn.cursor()
        cur.execute('SELECT count(*) FROM users WHERE user_id = %s and is_block = 0', (user_id,))
        in_db = cur.fetchone()[0]
        cur.close()
        conn.close()
        return in_db


class IsCourier(Filter):
    key = 'is_courier'

    async def check(self, m: types.Message):
        user_id = m.from_user.id
        conn = mysql_connection()
        cur = conn.cursor()
        cur.execute('SELECT count(*) FROM couriers WHERE user_id = %s', (user_id,))
        in_db = cur.fetchone()[0]
        cur.execute('SELECT count(*) FROM users WHERE user_id = %s and is_block = 0', (user_id,))
        is_not_block = cur.fetchone()[0]
        cur.close()
        conn.close()
        return in_db and is_not_block


class IsManager(Filter):
    key = 'is_manager'

    async def check(self, m: types.Message):
        user_id = m.from_user.id
        conn = mysql_connection()
        cur = conn.cursor()
        in_db = 1
        cur.execute('SELECT count(*) FROM users WHERE user_id = %s and is_block = 0 and city_id is not NULL', (user_id,))
        is_not_block = cur.fetchone()[0]
        cur.close()
        conn.close()
        return in_db and is_not_block or user_id in ADMINS
