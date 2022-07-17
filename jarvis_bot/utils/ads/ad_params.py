from keyboards.inline import dynamic_keyboards
from utils.ads.find_info import get_find_text
from utils.steps import define_step
from utils.steps.define_step import get_future_step


async def get_params_category(c, category_id):
    c.execute("select param_id, param_name, is_required, param_question "
              "from category_params where category_id = %s",
              (category_id,))
    all_params = c.fetchall()
    return all_params


async def get_step(c, message, ad_id, now_param_id=0, is_find=0, page_id=0):
    print(f'now_param_id: {now_param_id}')
    if now_param_id == 'brand':
        c.execute("select last_brand_id from ads where ad_id = %s", (ad_id,))
        last_brand_id = c.fetchone()[0]
        c.execute("select param_id "
                  "from brand_params where brand_id = %s order by param_position",
                  (last_brand_id,))
        first_param_id = c.fetchone()[0]
        inline_kb = await dynamic_keyboards.get_ad_param_keyboard(c, ad_id, first_param_id)
        c.execute("select question_text from params where param_id = %s", (first_param_id,))
        question_text = c.fetchone()[0]
        await message.edit_text(f'<b>{question_text}</b>',
                                reply_markup=inline_kb)
    else:
        new_param_id, old_param_id = await define_step.get_last_and_future(c, ad_id, now_param_id)
        print(f'old_param_idd: {old_param_id}')
        if new_param_id == 6:
            if is_find:
                await message.edit_text(f"{await get_find_text(c, ad_id)}",
                                        reply_markup=await dynamic_keyboards.edit_find_params(c, ad_id))
            else:
                message_text = "<b>Выберите время размещения объявления 👇</b>"
                inline_kb = await dynamic_keyboards.select_time_placing(c, ad_id,
                                                                        new_param_id, old_param_id)
                try:
                    await message.edit_text(message_text,
                                            reply_markup=inline_kb)
                except:
                    await message.answer(message_text,
                                         reply_markup=inline_kb)
        elif str(new_param_id).isdigit():
            # c.execute("select param_question, is_required from category_params where param_id = %s", (new_param_id,))
            # param_question, is_required = c.fetchone()
            # add_text = f'\n\n<i>* это не обязательный параметр и Вы можете пропустить его выбор</i>' if not \
            #     is_required else ''
            inline_kb = await dynamic_keyboards.get_ad_param_keyboard(c, ad_id, new_param_id, old_param_id=old_param_id)
            c.execute("select question_text from params where param_id = %s", (new_param_id,))
            question_text = c.fetchone()[0]
            await message.edit_text(f'<b>{question_text}</b>',
                                    reply_markup=inline_kb)
        elif str(new_param_id) == 'photo':
            message_text = f'<b>Выберите источник фото</b> 👇\n\n' \
                           f'💡 <i>\"Наше фото\" - фото, загруженное из интернета</i>'
            inline_kb = await dynamic_keyboards.select_type_photo(c, ad_id, old_param_id)
            try:
                await message.edit_text(text=message_text,
                                        reply_markup=inline_kb)
            except:
                await message.answer(text=message_text,
                                     reply_markup=inline_kb)
