import asyncio
import handlers

from aiogram import executor

from loader import dp
from data import config


if __name__ == '__main__':
    executor.start_polling(dp)
