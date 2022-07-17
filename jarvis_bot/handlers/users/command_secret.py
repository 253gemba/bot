from aiogram import types
from aiogram.dispatcher import FSMContext

from filters.filters import IsManager
from keyboards.default import default_keyboards
from keyboards.inline import dynamic_keyboards
from loader import dp
from states.states import AddInformation
from utils.db_api.python_mysql import mysql_connection


@dp.message_handler(IsManager(), commands=['secret'], state="*")
async def process_secret_command(message: types.Message, state: FSMContext):
    print(message)
    user_id = message.from_user.id
    msg_text = str(message.text)
    conn = mysql_connection()
    c = conn.cursor(buffered=True)
    await state.finish()
    c.execute("select brand_id from brand_params where category_id = 2 group by brand_id")
    all_brands = list(set([x[0] for x in c.fetchall()]))
    for one_brand in all_brands:
        for param_id in [3, 4, 6]:
            c.execute("select count(*) from brand_params where brand_id = %s and param_id = %s",
                      (one_brand, param_id))
            if not c.fetchone()[0]:
                c.execute("insert into brand_params (category_id, brand_id, param_id, option_id, param_position) "
                          "values (%s, %s, %s, %s, %s)",
                          (2, one_brand, param_id, 0, 5 if param_id == 3 else (4 if param_id == 4 else 2)))
                conn.commit()
    await message.answer(f'Выберите действие ⤵',
                         reply_markup=await dynamic_keyboards.add_type())
    c.close()
    conn.close()
