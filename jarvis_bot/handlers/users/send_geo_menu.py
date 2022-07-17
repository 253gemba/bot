from aiogram import types
from aiogram.dispatcher import FSMContext

from data import config
from keyboards.default import default_keyboards, default_buttons
from keyboards.inline import dynamic_keyboards
from loader import dp, bot
from states.states import SetCity
from utils.cities import nearest_towns
from utils.db_api.python_mysql import mysql_connection
from utils.excel.generate_report import do_file_db


@dp.message_handler(
    lambda message: message.text in default_keyboards.get_buttons_text_from_menu(default_keyboards.select_geo())
                    or message.location,
    content_types="any", state="*")
async def select_geo_menu_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    msg_text = str(message.text)
    conn = mysql_connection()
    c = conn.cursor(buffered=True)
    state_data = await state.get_data()
    state_state = await state.get_state()
    await state.finish()
    if msg_text == default_buttons.button_send_geo_hand.text:
        await message.answer("Выберите место, где живете 👇",
                             reply_markup=await dynamic_keyboards.area_or_region())
        # await message.answer('Выбери город 👇',
        #                      reply_markup=await nearest_towns.get_inline_kb(c, user_id, by_distance=0))
    elif msg_text == default_buttons.button_send_geo_auto.text or message.location:
        latitude = message.location.latitude
        longitude = message.location.longitude
        c.execute("update users set latitude = %s, longitude = %s where user_id = %s",
                  (latitude, longitude, user_id,))
        conn.commit()
        await message.answer("Укажите наиболее подходящую локацию 👇",
                             reply_markup=await nearest_towns.get_inline_kb(c, user_id,
                                                                            latitude=latitude,
                                                                            longitude=longitude))
    c.close()
    conn.close()
