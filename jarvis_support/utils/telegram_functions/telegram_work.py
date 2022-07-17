import urllib

import requests
from aiogram.types import InlineKeyboardMarkup, Message

from data import config
from data.config import BOT_TOKEN
from keyboards.default.default_keyboards import *
from loader import bot


def get_user_menu(c, user_id):
    c.execute("select count(*) from users where user_id = %s", (user_id,))
    is_client = c.fetchone()[0]
    if user_id in config.ADMINS:
        need_menu = admin_menu
    elif is_client:
        need_menu = client_menu
    # elif is_courier:
    #     c.execute("select is_active from couriers_list where user_id = %s", (user_id,))
    #     is_active_courier = c.fetchone()[0]
    #     need_menu = courier_menu
    # elif is_dispatcher:
    #     need_menu = partner_menu
    else:
        need_menu = user_menu
    return need_menu


async def get_bot_username():
    bot_username = await bot.get_me()
    return bot_username['username']


async def get_message_type(msg: Message):
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
    mailing_media_text = msg.html_text if msg.text else msg.caption_entities
    if not mailing_media_text:
        mailing_media_text = None
    return mailing_media_type, mailing_media_id, mailing_media_text


async def send_message_user(user_id, mailing_text, mailing_media_type, mailing_media_id, inline_buttons=None):
    try:
        if mailing_media_type:
            if mailing_media_type == 'gif':
                message_info = await bot.send_animation(chat_id=user_id,
                                                        caption=mailing_text,
                                                        animation=mailing_media_id,
                                                        reply_markup=InlineKeyboardMarkup(
                                                            inline_keyboard=inline_buttons))
            if mailing_media_type == 'video':
                message_info = await bot.send_video(chat_id=user_id,
                                                    caption=mailing_text,
                                                    video=mailing_media_id,
                                                    reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_buttons))
            if mailing_media_type == 'video_note':
                message_info = await bot.send_video_note(chat_id=user_id,
                                                         video_note=mailing_media_id,
                                                         reply_markup=InlineKeyboardMarkup(
                                                             inline_keyboard=inline_buttons))
            if mailing_media_type == 'audio':
                message_info = await bot.send_audio(chat_id=user_id,
                                                    caption=mailing_text,
                                                    audio=mailing_media_id,
                                                    reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_buttons))
            if mailing_media_type == 'voice':
                message_info = await bot.send_voice(chat_id=user_id,
                                                    caption=mailing_text,
                                                    voice=mailing_media_id,
                                                    reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_buttons))
            if mailing_media_type == 'doc':
                message_info = await bot.send_document(chat_id=user_id,
                                                       caption=mailing_text,
                                                       document=mailing_media_id,
                                                       reply_markup=InlineKeyboardMarkup(
                                                           inline_keyboard=inline_buttons))
            if mailing_media_type == 'photo':
                message_info = await bot.send_photo(chat_id=user_id,
                                                    caption=mailing_text,
                                                    photo=mailing_media_id,
                                                    reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_buttons))
        else:
            message_info = await bot.send_message(user_id,
                                                  f'{mailing_text}',
                                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_buttons),
                                                  disable_web_page_preview=True)
        return message_info
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
