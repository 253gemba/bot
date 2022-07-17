import urllib

import requests
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.deep_linking import encode_payload, decode_payload

from data.config import ADMINS, BOT_TOKEN
from keyboards.default.default_keyboards import *
from loader import bot


def get_user_role(c, user_id):
    c.execute("select count(*) from users where user_id = %s and city_id is not NULL", (user_id,))
    is_user = c.fetchone()[0]
    is_admin = user_id in ADMINS
    if is_admin:
        user_role = 'admin'
    elif is_user:
        user_role = 'user'
    else:
        user_role = 'no_reg'
    return user_role


def check_phone(phone_num):
    phone_num = str(phone_num)
    accept_symbols = "0123456789"
    phone_num = "".join([a if a in accept_symbols else "" for a in phone_num])
    one_cond = set(phone_num) < set(accept_symbols)
    two_cond = 10 < len(phone_num) < 12
    if phone_num[0] in ('7', '8'):
        phone_num = f'+7{phone_num[1:]}'
        three_cond = True
    else:
        three_cond = phone_num
    if one_cond and two_cond and three_cond:
        return phone_num
    else:
        return False


def get_user_menu(c, user_id):
    user_role = get_user_role(c, user_id)
    if user_role == 'admin':
        need_menu = admin_menu
    elif user_role == 'user':
        need_menu = ReplyKeyboardRemove()
    elif user_role == 'no_reg':
        need_menu = select_geo()
    else:
        need_menu = user_menu
    return need_menu


async def check_sub(user_id):
    result = await bot.get_chat_member(chat_id=config.CHECK_SUB_CHANNEL_ID,
                                       user_id=user_id)
    if result.is_chat_member():
        return True
    else:
        return False


async def create_link(role="manager", object_id=0):
    payload = encode_payload(f'{role}_{object_id}')
    link = f'https://t.me/{await get_bot_username()}?start={payload}'
    return link


async def decode_link(payload):
    decode_info = decode_payload(payload)
    return decode_info


async def get_bot_username():
    bot_username = await bot.get_me()
    return bot_username['username']


async def get_message_type(msg):
    try:
        mailing_media_id = msg.animation.file_id
        mailing_media_type = 'gif'
    except:
        try:
            mailing_media_id = msg.photo[-1].file_id
            mailing_media_type = 'photo'
        except:
            try:
                mailing_media_id = msg.video.file_id
                mailing_media_type = 'video'
            except:
                try:
                    mailing_media_id = msg.video_note.file_id
                    mailing_media_type = 'video_note'
                except:
                    try:
                        mailing_media_id = msg.audio.file_id
                        mailing_media_type = 'audio'
                    except:
                        try:
                            mailing_media_id = msg.document.file_id
                            mailing_media_type = 'doc'
                        except:
                            try:
                                mailing_media_id = msg.voice.file_id
                                mailing_media_type = 'voice'
                            except:
                                mailing_media_id = None
                                mailing_media_type = None
    return mailing_media_type, mailing_media_id


async def send_message_user(user_id, mailing_text, mailing_media_type, mailing_media_id, inline_buttons=None):
    try:
        if mailing_media_type:
            if mailing_media_type == 'gif':
                await bot.send_animation(chat_id=user_id,
                                         caption=mailing_text,
                                         animation=mailing_media_id,
                                         reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_buttons))
            if mailing_media_type == 'video':
                await bot.send_video(chat_id=user_id,
                                     caption=mailing_text,
                                     video=mailing_media_id,
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_buttons))
            if mailing_media_type == 'video_note':
                await bot.send_video_note(chat_id=user_id,
                                          video_note=mailing_media_id,
                                          reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_buttons))
            if mailing_media_type == 'audio':
                await bot.send_audio(chat_id=user_id,
                                     caption=mailing_text,
                                     audio=mailing_media_id,
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_buttons))
            if mailing_media_type == 'voice':
                await bot.send_voice(chat_id=user_id,
                                     caption=mailing_text,
                                     voice=mailing_media_id,
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_buttons))
            if mailing_media_type == 'doc':
                await bot.send_document(chat_id=user_id,
                                        caption=mailing_text,
                                        document=mailing_media_id,
                                        reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_buttons))
            if mailing_media_type == 'photo':
                await bot.send_photo(chat_id=user_id,
                                     caption=mailing_text,
                                     photo=mailing_media_id,
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_buttons))
        else:
            await bot.send_message(user_id,
                                   f'{mailing_text}',
                                   reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_buttons),
                                   disable_web_page_preview=True)
        return True
    except:
        return False


async def get_link_photo(file_id):
    file_path = await bot.get_file(file_id)
    photo = 'https://api.telegram.org/file/bot{0}/{1}'.format(BOT_TOKEN, file_path['file_path'])
    # gcontext = ssl.SSLContext()
    with urllib.request.urlopen(photo) as response:
        data = response.read()  # a `bytes` object
        try:
            photo = 'https://telegra.ph{0}'.format(requests.post('https://telegra.ph/upload',
                                                                 files={
                                                                     'file': ('file', data, 'image/jpeg')
                                                                 }).json()[0]['src'])
        except Exception as e:
            print(e)
            photo = ''
    return photo
