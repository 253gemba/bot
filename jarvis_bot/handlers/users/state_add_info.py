import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.inline import dynamic_keyboards
from loader import dp
from states.states import *
from utils.db_api.python_mysql import mysql_connection


@dp.message_handler(content_types="any", state=AddInformation.all_states)
async def add_money(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    msg_text = message.text
    conn = mysql_connection()
    c = conn.cursor(buffered=True)
    state_name = await state.get_state()
    state_data = await state.get_data()
    logging.info(f'{user_id} {msg_text}')
    info_type = state_data.get('info_type')
    param_id = state_data.get('param_id')
    brand_id = state_data.get('brand_id')
    if info_type == 'params':
        for one_param in msg_text.split("\n"):
            one_param = one_param.strip()
            if one_param:
                c.execute("select count(*) from options where option_name = %s and param_id = %s",
                          (one_param, param_id))
                if not c.fetchone()[0]:
                    c.execute("insert into options (param_id, option_name) values (%s, %s)",
                              (param_id, one_param))
                    conn.commit()
    elif info_type == 'options':
        for one_param in msg_text.split("\n"):
            one_param = one_param.strip()
            c.execute("select option_id from options where param_id = %s and option_name = %s",
                      (param_id, one_param,))
            option_id = c.fetchone()[0]
            c.execute("select category_id from brands where brand_id = %s",
                      (brand_id,))
            category_id = c.fetchone()[0]
            if one_param:
                c.execute("select count(*) from brand_params "
                          "where brand_id = %s and param_id = %s and option_id = %s",
                          (brand_id, param_id, option_id))
                if not c.fetchone()[0]:
                    c.execute("insert into brand_params (param_id, brand_id, option_id, category_id) "
                              "values (%s, %s, %s, %s)",
                              (param_id, brand_id, option_id, category_id))
                    conn.commit()
    elif info_type == 'brands':
        c.execute("select category_id, is_serial, is_model, parent_id from brands where brand_id = %s", (brand_id,))
        category_id, parent_is_serial, parent_is_model, parent_parent_id = c.fetchone()
        if parent_is_serial:
            is_serial = 0
            is_model = 1
        elif parent_is_model:
            raise
        else:
            is_serial = 1
            is_model = 0
        for one_param in msg_text.split("\n"):
            one_param = one_param.strip()
            if one_param:
                c.execute("select count(*) from brands where brand_name = %s and parent_id = %s",
                          (one_param, brand_id))
                if not c.fetchone()[0]:
                    c.execute("insert into brands (category_id, parent_id, brand_name, is_serial, is_model) "
                              "values (%s, %s, %s, %s, %s)",
                              (category_id, brand_id, one_param, is_serial, is_model))
                    conn.commit()
    elif info_type == 'brands_params':
        for one_model in msg_text.split("\n"):
            one_model = one_model.strip()
            param_params = one_model.split('  ')

            model_name = param_params[0].strip()
            model_params = param_params[1:]

            c.execute("select count(*) from brands where brand_name = %s and parent_id = %s", (model_name, brand_id))
            if not c.fetchone()[0]:
                c.execute("insert into brands (brand_name, parent_id) values (%s, %s)",
                          (model_name, brand_id))
                conn.commit()
            c.execute("select brand_id, category_id "
                      "from brands where brand_name = %s and parent_id = %s", (model_name, brand_id))
            model_id, category_id = c.fetchone()
            for one_param in model_params:
                one_param = one_param.strip()
                c.execute("select param_id, option_id from options where option_name = %s",
                          (one_param,))
                try:
                    param_id, option_id = c.fetchone()
                    c.execute("select count(*) from brand_params "
                              "where param_id = %s and option_id = %s and brand_id = %s",
                              (param_id, option_id, model_id))

                    # assert 1 == 0
                    if not c.fetchone()[0]:
                        c.execute("insert into brand_params (category_id, brand_id, param_id, "
                                  "option_id, param_position) "
                                  "values (%s, %s, %s, %s, %s)",
                                  (category_id, model_id, param_id, option_id,
                                   1 if param_id == 1 else (3 if param_id == 2 else 0)))
                    conn.commit()
                except Exception as e:
                    logging.info(f'{e, model_name, one_param}')
                    pass
    await message.answer("Успех ✅")
    if info_type == 'params':
        await message.answer(f'Выберите параметр',
                             reply_markup=await dynamic_keyboards.params_for_admin(c))
    elif info_type in ('brands', 'brands_params'):
        await message.answer(f'Выберите бренд',
                             reply_markup=await dynamic_keyboards.brands_for_admin(c))
    c.close()
    conn.close()
