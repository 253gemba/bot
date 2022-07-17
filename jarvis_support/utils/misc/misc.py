import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage

storage = RedisStorage('localhost', 6379, db=10)
PROXY_URL = None
admins = (128885673, 292121432)
token = "1493423072:AAHuAexUHY1ao0G1zYKxh15DM7F5bsoDEYs"
bot = Bot(token=token, proxy=PROXY_URL, parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(format=u'%(filename)s [ LINE:%(lineno)+3s ]#%(levelname)+8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)