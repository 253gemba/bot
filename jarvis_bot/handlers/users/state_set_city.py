import logging
import transliterate
from aiogram import types

from aiogram.dispatcher import FSMContext
from aiogram.types import InlineQuery, InputTextMessageContent, InlineQueryResultArticle
from mysql.connector import MySQLConnection

from data import config
from keyboards.default import default_keyboards, default_buttons
from keyboards.inline import dynamic_keyboards
from loader import dp, bot
from states.states import SetCity
from utils.cities.db_cities import check_city_by_name
from utils.db_api.python_mysql import read_db_config, mysql_connection
from utils.default_tg.default import get_user_menu


@dp.inline_handler(state=SetCity.all_states)
async def inline_echo(msg: InlineQuery, state: FSMContext):
    inline_text = msg.query
    # CONNECT TO DATABASE
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    c = conn.cursor(buffered=True)
    state_data = await state.get_data()
    state_state = await state.get_state()
    inline_text = str(inline_text).strip()

    city_type = state_data['city_type']
    if state_state == SetCity.area.state:
        all_city_names = await check_city_by_name(c, inline_text, city_type)
    else:
        all_city_names = await check_city_by_name(c, inline_text, city_type, city_area=state_data['area_id'])
    items = []
    items_titles = []
    in_list = []
    if len(inline_text) >= 0:
        for x in all_city_names[:50]:

            try:
                if state_state == SetCity.area.state:
                    city_id, city_name = x
                    # print(x)
                    content_text = city_name
                    input_content = InputTextMessageContent(f'city_type_id:{city_id}')
                elif state_state == SetCity.city.state:
                    city_id, city_name = x
                    # print(x)
                    content_text = city_name
                    input_content = InputTextMessageContent(f'city_id:{city_id}')
                else:
                    content_text = None
                    input_content = None
                title = str(content_text)
                item = InlineQueryResultArticle(
                    id=all_city_names.index(x),
                    title=title,
                    input_message_content=input_content
                )
                items.append(item)
                items_titles.append(title)
            except Exception as e:
                logging.info(e)
        if len(items) == 0:
            input_content = InputTextMessageContent(f'Ничего не найдено')
            title = f'Ничего не найдено :('
            item = InlineQueryResultArticle(
                id='not_find',
                title=title,
                input_message_content=input_content
            )
            if inline_text != '':
                items.append(item)
        await bot.answer_inline_query(msg.id, results=items, cache_time=1)
    c.close()
    conn.close()


@dp.message_handler(lambda message: "/" not in message.text,
                    content_types="any", state=SetCity.all_states)
async def state_set_city(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    msg_text = message.text
    conn = mysql_connection()
    c = conn.cursor(buffered=True)
    state_name = await state.get_state()
    state_data = await state.get_data()
    logging.info(f'{msg_text} {user_id}')
    if state_name == SetCity.area.state:
        await message.delete()
        area_id = msg_text.split(":")[1]
        await state.update_data(area_id=area_id)
        await state.update_data(city_type='city')
        await SetCity.next()
        await message.answer("Нажмите на кнопку ниже и начните вводить город",
                             reply_markup=await dynamic_keyboards.find_city('city'))
    else:
        city_id = msg_text.split(":")[1]
        c.execute("update users set city_id = %s where user_id = %s", (city_id, user_id))
        conn.commit()
        await state.finish()
        await message.delete()
        await message.answer(f"Город выбран ✅\n\n"
                             f"Теперь при просмотре объявления, установке оповещения или подаче объявления "
                             f"будет указываться этот город.\n\n"
                             f"Изменить город можно в разделе ПРОФИЛЬ",
                             reply_markup=default_keyboards.ReplyKeyboardRemove())
        c.execute("select bonus_value, is_get_bonus from users where user_id = %s", (user_id,))
        bonus_value, is_get_bonus = c.fetchone()
        if not is_get_bonus:
            c.execute("update users set balance = balance + %s, is_get_bonus = 1 "
                      "where user_id = %s", (bonus_value, user_id))
            conn.commit()
            if bonus_value:
                await message.answer(f"💰 <b>Вы получили бонус! {bonus_value} РУБ уже на Вашем счету!</b>")
        await message.answer("Теперь ознакомьтесь с кратким гайдом и попробуйте подать или найти объявления 👇")
        await message.answer(f"<b>/{config.COMMANDS[0][0]}</b> - найти объявление\n"
                             f"<b>/{config.COMMANDS[1][0]}</b> - подать объявления\n"
                             f"<b>/{config.COMMANDS[2][0]}</b> - настроить оповещения\n"
                             f"<b>/{config.COMMANDS[3][0]}</b> - изменить город, баланс\n"
                             f"<b>/{config.COMMANDS[4][0]}</b> - задать вопрос",
                             reply_markup=get_user_menu(c, user_id))
    c.close()
    conn.close()
