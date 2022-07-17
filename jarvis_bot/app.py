import asyncio
import handlers

from aiogram import executor

from loader import dp
from utils.commands.manage_commands import on_startup_notify


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    executor.start_polling(dp, loop=loop, on_startup=on_startup_notify)
