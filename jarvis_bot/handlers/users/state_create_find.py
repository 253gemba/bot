import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.default import default_buttons
from keyboards.inline import dynamic_keyboards
from loader import dp
from states.states import *
from utils.ads.find_info import get_find_text
from utils.db_api.python_mysql import mysql_connection


@dp.message_handler(content_types="any", state=CreateFind.all_states)
async def create_find_form(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    msg_text = message.text
    conn = mysql_connection()
    c = conn.cursor(buffered=True)
    state_name = await state.get_state()
    state_data = await state.get_data()
    logging.info(f'{user_id} {msg_text}')
    try:
        object_id = state_data['object_id']
    except:
        object_id = 0
    if msg_text == default_buttons.button_reset_ad.text:
        await message.answer("⚠ <b>Вы действительно хотите сбросить заполненный прогресс?</b>",
                             reply_markup=dynamic_keyboards.delete_object(f'resetAd_{object_id}_{0}'))
    elif object_id:
        param_id = state_data['param_id']
        if state_name == CreateFind.edit_options.state:
            if param_id == 'price':
                try:
                    c.execute("update finds set price_limit_id = %s, max_price = %s where find_id = %s",
                              (msg_text.split('-')[0], msg_text.split('-')[1], object_id))
                    conn.commit()
                    await state.finish()
                    await message.answer(f"{await get_find_text(c, object_id)}",
                                         reply_markup=await dynamic_keyboards.edit_find_params(c, object_id))
                except:
                    await message.answer("⚠ Цена должна быть указана в формате 1000-100000 - от минимальной до "
                                         "максимальной со знаком тире")
            else:
                c.execute("select count(*) from find_options where find_id = %s and option_id = %s",
                          (object_id, param_id))
                if c.fetchone()[0]:
                    c.execute("update find_options set option_value = %s "
                              "where find_id = %s and param_id = %s",
                              (msg_text, object_id, param_id))
                else:
                    c.execute("insert into find_options (option_value,  find_id, param_id) "
                              "values (%s, %s, %s)",
                              (msg_text, object_id, param_id))
                conn.commit()
                await state.finish()
                await message.answer(f"{await get_find_text(c, object_id)}",
                                     reply_markup=await dynamic_keyboards.edit_find_params(c, object_id))
    conn.commit()
    c.close()
    conn.close()
