import asyncio
import logging

from aiogram import Dispatcher
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats

from data import config
from data.config import ADMINS
from loader import bot
from utils.db_api.python_mysql import mysql_connection
from utils.external_systems.yookassa_payments import update_payments
from utils.find.make_find import check_notifications
from utils.mailing.mailing import go_mailing


async def set_commands():
    commands = []
    for one_command in config.COMMANDS:
        commands.append(BotCommand(command=one_command[0],
                                   description=one_command[1]))
    scope = BotCommandScopeAllPrivateChats()
    await bot.set_my_commands(commands=commands,
                              scope=scope)


async def menu_update_reminder():
    while True:
        try:
            conn = mysql_connection()
            c = conn.cursor(buffered=True)
            await update_payments(c, conn)
            await check_notifications(c, conn)
            c.execute("select mail_id, city_id from mailing "
                      "where is_sent = 0 and mail_datetime < date_add(UTC_TIMESTAMP(), interval 3 hour)")
            try:
                mail_id, city_id = c.fetchone()
            except:
                mail_id, city_id = None, None
            if 'obl' in str(city_id):
                c.execute("select city_id from all_cities "
                          "where city_area = (select city_area from all_cities where city_id = %s)",
                          (city_id.split("obl")[1],))
                mailing_cities = [x[0] for x in c.fetchall()]
            else:
                mailing_cities = [city_id]
            c.close()
            conn.close()
            if mail_id:
                await go_mailing(mailing_id=mail_id, cities=mailing_cities)
        except Exception as e:
            logging.info(e)
        await asyncio.sleep(30)


async def on_startup_notify(dp: Dispatcher):
    # asyncio.create_task(check_orders())
    await set_commands()
    # for admin in ADMINS:
    #     try:
    #         await dp.bot.send_message(admin, "Бот обновлен")
    #     except Exception as err:
    #         pass
    asyncio.create_task(menu_update_reminder())
