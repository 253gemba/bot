import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

from filters.filters import IsManager
from keyboards.default import default_keyboards, default_buttons
from keyboards.inline import dynamic_keyboards
from loader import dp, bot
from states.states import CreateAd
from utils.db_api.python_mysql import mysql_connection
from utils.default_tg.default import get_user_menu


@dp.message_handler(IsManager(),
                    lambda message: message.text in default_keyboards.get_buttons_text_from_menu(
                        default_keyboards.user_menu),
                    content_types="any", state="*")
async def user_menu_header(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    msg_text = str(message.text)
    conn = mysql_connection()
    c = conn.cursor(buffered=True)
    logging.info(f'{user_id} {msg_text}')
    state_data = await state.get_data()
    state_state = await state.get_state()
    await state.finish()
    if msg_text == default_buttons.button_my_profile.text:
        await bot.send_message(user_id,
                               f'Выберите действие ⤵',
                               reply_markup=default_keyboards.my_profile_menu)
    elif msg_text == default_buttons.button_help.text:
        await message.answer("Напишите Ваш вопрос или пожелание",
                             reply_markup=default_keyboards.cancel_operation_menu)
    elif msg_text == default_buttons.button_find_ads.text:
        await message.answer("Раздел недоступен",
                             reply_markup=get_user_menu(c, user_id))
    elif msg_text == default_buttons.button_add_ad.text:
        await message.answer("Раздел недоступен",
                             reply_markup=get_user_menu(c, user_id))
    elif msg_text == default_buttons.button_my_ads.text:
        await message.answer("Раздел недоступен",
                             reply_markup=get_user_menu(c, user_id))
    c.close()
    conn.close()
