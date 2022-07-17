import asyncio
import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InputMedia, MediaGroup

from data import config
from keyboards.default import default_keyboards, default_buttons
from keyboards.inline import dynamic_keyboards
from loader import dp, bot
from states.states import CreateAd, AddMoney, SetCity, CreateFind, AddInformation
from utils.ads import ad_info, ad_params, find_info
from utils.ads.ad_info import show_ads
from utils.ads.find_info import get_find_text
from utils.cities import nearest_towns
from utils.db_api.python_mysql import mysql_connection
from utils.default_tg.default import get_user_menu
from utils.external_systems.yookassa_payments import create_payment
from utils.find.make_find import find_results
from utils.steps import define_step, step_messages


@dp.callback_query_handler(state="*")
async def process_callback_messages(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    query_id = callback_query.id
    conn = mysql_connection()
    c = conn.cursor(buffered=True)
    try:
        message_id = callback_query.message.message_id
    except:
        message_id = callback_query.inline_message_id
    query_data = callback_query.data
    message = callback_query.message
    print(f'CallbackQuery: {user_id} -> {query_data}')
    start_data = query_data.split('_')[0]
    close_kb = [
        [InlineKeyboardButton(text=f'Закрыть ✖',
                              callback_data=f'hide')]
    ]
    try:
        null_param = query_data.split('_')[0]
    except:
        null_param = None
    try:
        one_param = query_data.split('_')[1]
    except:
        one_param = None
    try:
        two_param = query_data.split('_')[2]
    except:
        two_param = None
    try:
        three_param = query_data.split('_')[3]
    except:
        three_param = None
    try:
        four_param = query_data.split('_')[4]
    except:
        four_param = None
    if 'hide' == start_data:
        await state.finish()
        await bot.delete_message(user_id, message_id)
        if one_param:
            for message_id_to_delete in query_data.split("_")[1:]:
                await bot.delete_message(user_id, message_id_to_delete)

    elif 'addMoney' == start_data:
        await AddMoney.first()
        await message.answer("Введите сумму пополнения баланса. Например, 1200",
                             reply_markup=default_keyboards.cancel_operation_menu)

    elif 'createAd' == start_data:
        create_state = one_param
        ad_id = two_param if not two_param else int(two_param)
        is_edit = 0 if not three_param else int(three_param)
        if create_state == 'category':
            await message.answer("Выберите категорию",
                                 reply_markup=await dynamic_keyboards.get_categories(c))
        elif 'section' in create_state:
            parent_id = int(create_state.split(':')[1])
            await message.answer("Выберите раздел",
                                 reply_markup=await dynamic_keyboards.get_categories(c, parent_id))

    elif 'editBrandFind' == start_data:
        find_id = one_param
        brand_id = two_param
        c.execute("select is_serial, is_model "
                  "from brands where brand_id = %s", (brand_id,))
        now_is_serial, now_is_model = c.fetchone()
        if now_is_serial:
            c.execute("update finds set serial_id = %s where find_id = %s", (brand_id, find_id))
        elif now_is_model:
            c.execute("update finds set model_id = %s where find_id = %s", (brand_id, find_id))
        else:
            c.execute("update finds set brand_id = %s where find_id = %s", (brand_id, find_id))
        conn.commit()
        c.execute("delete from find_brands where find_id = %s", (find_id,))
        c.execute("delete from find_options where find_id = %s", (find_id,))
        conn.commit()
        all_ads = await find_results(c, find_id)
        await message.edit_text(f"{await get_find_text(c, one_param, count_ads=len(all_ads))}",
                                reply_markup=await dynamic_keyboards.edit_find_params(c, one_param,
                                                                                      count_ads=len(all_ads)))

    elif 'selectClosesParamOptionPage' == start_data:
        await message.edit_reply_markup(await dynamic_keyboards.get_sizes(c, one_param, int(three_param),
                                                                          two_param, int(four_param)))

    elif 'selectBrandAd' == start_data:
        ad_id = one_param
        brand_id = two_param
        c.execute("select is_serial, is_model, category_id, parent_id "
                  "from brands where brand_id = %s", (brand_id,))
        now_is_serial, now_is_model, category_id, brand_parent_id = c.fetchone()
        c.execute("update ads set last_brand_id = %s where ad_id = %s", (brand_id, ad_id))
        if now_is_serial:
            c.execute("update ads set serial_id = %s where ad_id = %s", (brand_id, ad_id))
        elif now_is_model:
            c.execute("update ads set model_id = %s where ad_id = %s", (brand_id, ad_id))
        else:
            c.execute("update ads set brand_id = %s where ad_id = %s", (brand_id, ad_id))
        conn.commit()
        if not now_is_model and not now_is_serial and not brand_parent_id:
            c.execute("update ads set main_brand_id = %s where ad_id = %s", (brand_id, ad_id))
            conn.commit()
        c.execute("select count(*) from brands where parent_id = %s", (brand_id,))
        if c.fetchone()[0]:
            inline_kb = await dynamic_keyboards.get_brands(c, ad_id, parent_id=brand_id)
            c.execute("select is_serial, is_model "
                      "from brands where parent_id = %s", (brand_id,))
            is_serial, is_model = c.fetchone()
            await message.edit_text(text=f'<b>Выберите '
                                         f'{"корпус" if category_id == -1 else ("серию" if is_serial else "модель")} '
                                         f'👇</b>',
                                    reply_markup=inline_kb)
        else:
            c.execute("select last_brand_id from ads where ad_id = %s", (ad_id,))
            last_brand_id = c.fetchone()[0]
            print(last_brand_id)
            c.execute("select param_id "
                      "from brand_params where brand_id = %s order by param_position",
                      (last_brand_id,))
            first_param_id = c.fetchone()[0]
            if first_param_id == 6:
                await message.edit_text(f'<b>Выберите время размещения</b> 👇',
                                        reply_markup=await dynamic_keyboards.select_time_placing(c, ad_id, 0, 0))
            else:
                inline_kb = await dynamic_keyboards.get_ad_param_keyboard(c, ad_id, first_param_id)
                c.execute("select question_text from params where param_id = %s", (first_param_id,))
                question_text = c.fetchone()[0]
                await message.edit_text(f'<b>{question_text}</b>',
                                        reply_markup=inline_kb)

    elif 'selectClothesBrand' == start_data:
        object_id = one_param
        brand_id = two_param
        is_find = int(three_param)
        if is_find:
            c.execute("update finds set brand_id = %s where find_id = %s", (brand_id, object_id))
            c.execute("select section_id, closes_body_part, closes_type from finds where find_id = %s",
                      (object_id,))
        else:
            c.execute("update ads set brand_id = %s where ad_id = %s", (brand_id, object_id))
            c.execute("select section_id, closes_body_part, closes_type from ads where ad_id = %s",
                      (object_id,))
        section_id, closes_body_part, closes_type = c.fetchone()
        conn.commit()
        c.execute("select count(*) from closes_types "
                  "where category_id = %s and IF(%s, parent_id = %s, parent_id is NULL) and "
                  "body_part = %s and is_type = 1",
                  (section_id, closes_type, closes_type, closes_body_part))
        if c.fetchone()[0]:
            await message.edit_text("<b>Выберите тип одежды</b> 👇",
                                    reply_markup=await dynamic_keyboards.closes_types(c, object_id, is_find=is_find))
        else:
            await message.edit_text("<b>Выберите вид</b> 👇",
                                    reply_markup=await dynamic_keyboards.closes_types(c, object_id, is_find=is_find,
                                                                                      is_type=0))

    elif 'typeBrandClothes' == start_data:
        ad_id = one_param
        is_find = int(two_param)
        await message.edit_text("<b>Выберите бренд одежды</b> 👇",
                                reply_markup=await dynamic_keyboards.clothes_brands(c, ad_id, is_find=is_find,
                                                                                    select_brand=1))

    elif 'selectPartClothes' == start_data:
        object_id = one_param
        is_find = int(two_param)
        brand_id = None
        if is_find:
            c.execute("update finds set brand_id = %s, closes_type = NULL where find_id = %s", (brand_id, object_id))
            conn.commit()
            c.execute("select section_id, closes_body_part, closes_type from finds where find_id = %s",
                      (object_id,))
        else:
            c.execute("update ads set brand_id = %s, closes_type = NULL where ad_id = %s", (brand_id, object_id))
            conn.commit()
            c.execute("select section_id, closes_body_part, closes_type from ads where ad_id = %s",
                      (object_id,))
        section_id, closes_body_part, closes_type = c.fetchone()
        c.execute("select count(*) from closes_types "
                  "where category_id = %s and IF(%s, parent_id = %s, parent_id is NULL) and "
                  "body_part = %s and is_type = 1",
                  (section_id, closes_type, closes_type, closes_body_part))
        if c.fetchone()[0]:
            await message.edit_text("<b>Выберите тип одежды</b> 👇",
                                    reply_markup=await dynamic_keyboards.closes_types(c, object_id, is_find=is_find))
        else:
            await message.edit_text("<b>Выберите вид</b> 👇",
                                    reply_markup=await dynamic_keyboards.closes_types(c, object_id, is_find=is_find,
                                                                                      is_type=0))

    elif 'selectClosesType' == start_data:
        object_id = one_param
        type_id = int(two_param)
        is_find = int(three_param)
        if is_find:
            c.execute("update finds set closes_type = %s where find_id = %s", (type_id, object_id))
            conn.commit()
            c.execute("select section_id, closes_body_part, closes_type from finds where find_id = %s",
                      (object_id,))
        else:
            c.execute("update ads set closes_type = %s where ad_id = %s", (type_id, object_id))
            conn.commit()
            c.execute("select section_id, closes_body_part, closes_type from ads where ad_id = %s",
                      (object_id,))
        section_id, closes_body_part, closes_type = c.fetchone()
        c.execute("select count(*) from closes_types "
                  "where category_id = %s and IF(%s, parent_id = %s, parent_id is NULL) and "
                  "body_part = %s and is_type = 0",
                  (section_id, closes_type, closes_type, closes_body_part))
        if c.fetchone()[0]:
            await message.edit_text("<b>Выберите вид</b> 👇",
                                    reply_markup=await dynamic_keyboards.closes_types(c, object_id, is_find=is_find,
                                                                                      is_type=0))
        else:
            await message.edit_text("<b>Выберите раздел</b> 👇",
                                    reply_markup=await dynamic_keyboards.get_size_format(c, object_id, is_find=is_find))

    elif 'selectClosesKind' == start_data:
        ad_id = one_param
        type_id = int(two_param)
        is_find = int(three_param)
        if is_find:
            c.execute("update finds set closes_kind = %s where find_id = %s", (type_id, ad_id))
            conn.commit()
        else:
            c.execute("update ads set closes_kind = %s where ad_id = %s", (type_id, ad_id))
            conn.commit()
        await message.edit_text("<b>Выберите раздел</b> 👇",
                                reply_markup=await dynamic_keyboards.get_size_format(c, ad_id, is_find=is_find))

    elif 'setSizeType' == start_data:
        object_id = one_param
        size_type = two_param
        is_find = int(three_param)
        if is_find:
            c.execute("update finds set closes_size_type = %s where find_id = %s", (size_type, object_id))
            conn.commit()
            c.execute("select category_id, section_id, closes_body_part, closes_size_type from finds "
                      "where find_id = %s", (object_id,))
        else:
            c.execute("update ads set closes_size_type = %s where ad_id = %s", (size_type, object_id))
            conn.commit()
            c.execute("select category_id, section_id, closes_body_part, closes_size_type from ads "
                      "where ad_id = %s", (object_id,))
        category_id, section_id, closes_body_part, closes_size_type = c.fetchone()
        if closes_size_type == 'eu':
            param_id = 16
        elif closes_size_type == 'usa':
            param_id = 17
        elif closes_size_type == 'numeric':
            param_id = 14
        else:
            param_id = 15
        await message.edit_text("<b>Выберите размер</b> 👇",
                                reply_markup=await dynamic_keyboards.get_sizes(c, object_id,
                                                                               param_id=param_id, is_find=is_find))

    elif 'selectClosesParamOption' == start_data:
        object_id = one_param
        param_id = int(two_param)
        option_id = int(three_param)
        is_find = int(four_param)
        if is_find:
            c.execute("select count(*) from find_options where param_id = %s and option_id = %s and find_id = %s",
                      (param_id, option_id, object_id))
            if c.fetchone()[0]:
                c.execute("delete from find_options where param_id = %s and option_id = %s and find_id = %s",
                          (param_id, option_id, object_id))
            else:
                c.execute("insert into find_options (param_id, option_id, find_id) values (%s, %s, %s)",
                          (param_id, option_id, object_id))
            conn.commit()
        else:
            c.execute("select count(*) from ad_options where param_id = %s and ad_id = %s",
                      (param_id, object_id))
            if c.fetchone()[0]:
                c.execute("delete from ad_options where param_id = %s and ad_id = %s",
                          (param_id, object_id))
            else:
                c.execute("insert into ad_options (param_id, option_id, ad_id) values (%s, %s, %s)",
                          (param_id, option_id, object_id))
            conn.commit()
        if is_find:
            await message.edit_reply_markup(reply_markup=await dynamic_keyboards.get_sizes(c, object_id,
                                                                                           is_find=is_find,
                                                                                           param_id=param_id))
        else:
            if param_id == 3:
                await message.delete()
                await CreateAd.first()
                await state.update_data(object_id=object_id)
                await message.answer("📷 <b>Загрузите до 10 фото</b>",
                                     reply_markup=default_keyboards.ad_price_menu)
            else:
                await message.edit_text("<b>Выберите срок размещения</b> ⤵",
                                        reply_markup=await dynamic_keyboards.closes_time_placing(c, object_id,
                                                                                                 is_find))

    # elif 'selectClothesBrand' == start_data:
    #     ad_id = one_param
    #     await message.edit_text("<b>Выберите раздел</b> 👇",
    #                             reply_markup=await dynamic_keyboards.clothes_brands(c, ad_id, is_find=0,
    #                                                                                 is_closes_part=1,
    #                                                                                 select_brand=1))

    elif 'setBodyPart' == start_data:
        ad_id = one_param
        body_part = two_param
        is_find = int(three_param)
        if is_find:
            c.execute("update finds set closes_body_part = %s, closes_type = NULL "
                      "where find_id = %s", (body_part, ad_id))
            conn.commit()
        else:
            c.execute("update ads set closes_body_part = %s, closes_type = NULL "
                      "where ad_id = %s", (body_part, ad_id))
            conn.commit()
        await message.edit_text("<b>Одежда должна быть брендовая</b>?",
                                reply_markup=await dynamic_keyboards.get_brand_type(c, ad_id, is_find=is_find))

    elif 'placeTime' == start_data:
        object_id = int(one_param)
        place_days_period = int(two_param)
        is_find = int(three_param)
        c.execute("select balance from users where user_id = %s", (user_id,))
        balance = c.fetchone()[0]
        if is_find:
            c.execute("select section_id, category_id from finds where find_id = %s", (object_id,))
            section_id, category_id = c.fetchone()
            c.execute("select tariff_notify_first, tariff_notify_second "
                      "from categories where category_id = %s", (section_id,))
            tariff_first_price, tariff_second_price = c.fetchone()
        else:
            c.execute("select section_id, category_id from ads where ad_id = %s", (object_id,))
            section_id, category_id = c.fetchone()
            c.execute("select tariff_first_price, tariff_second_price "
                      "from categories where category_id = %s", (section_id,))
            tariff_first_price, tariff_second_price = c.fetchone()
        tariff_price = tariff_first_price if place_days_period == 15 else tariff_second_price
        if balance >= tariff_price:
            c.execute("update ads set place_days_period = %s, tariff_price = %s where ad_id = %s",
                      (place_days_period, tariff_price, object_id,))
            conn.commit()
            if is_find:
                pass
            else:
                await message.edit_text("<b>Оцените состояние товара</b>",
                                        reply_markup=await dynamic_keyboards.get_sizes(c, object_id,
                                                                                       param_id=3,
                                                                                       is_find=is_find))
        else:
            await message.answer(f"⚠ <b>Недостаточно средств на балансе</b>\n\n"
                                 f"Необходимо {tariff_price}₽, но у Вас только {balance}₽",
                                 reply_markup=dynamic_keyboards.balance_menu())

    elif 'createAdSelectCategory' == start_data:
        if two_param:
            c.execute("select city_id from users where user_id = %s", (user_id,))
            city_id = c.fetchone()[0]
            c.execute("insert into ads (category_id, section_id, user_id, city_id) values (%s, %s, %s, %s)",
                      (one_param, two_param, user_id, city_id))
            conn.commit()
            ad_id = c.lastrowid
            # all_category_params = await get_params_category(c, two_param)
            # new_param_id = all_category_params[0][0]
            if int(one_param) == 6:
                inline_kb = await dynamic_keyboards.get_brands(c, ad_id, is_find=0)
            else:
                inline_kb = await dynamic_keyboards.get_body_parts(c, ad_id, is_find=0)
            await message.edit_text(text=f'<b>Выберите {"марку" if int(one_param) != 14 else "часть тела"} 👇</b>',
                                    reply_markup=inline_kb)
        elif int(one_param):
            await message.edit_text("<b>В каком разделе нужно разместить объявление?</b> ⤵",
                                    reply_markup=await dynamic_keyboards.get_categories(c, one_param))
        else:
            await message.edit_text("<b>В какой категории Вы бы хотели подать объявление?</b> ⤵",
                                    reply_markup=await dynamic_keyboards.get_categories(c))

    elif 'selectBrandFind' == start_data:
        find_id = one_param
        brand_id = two_param
        c.execute("select is_serial, is_model, category_id "
                  "from brands where brand_id = %s", (brand_id,))
        now_is_serial, now_is_model, category_id = c.fetchone()
        c.execute("update finds set last_brand_id = %s where find_id = %s", (brand_id, find_id))
        if now_is_serial:
            c.execute("update finds set serial_id = %s where find_id = %s", (brand_id, find_id))
        elif now_is_model:
            c.execute("update finds set model_id = %s where find_id = %s", (brand_id, find_id))
        else:
            c.execute("update finds set brand_id = %s where find_id = %s", (brand_id, find_id))
        conn.commit()
        c.execute("select brand_id from finds where find_id = %s", (find_id,))
        db_brand_id = c.fetchone()[0]
        c.execute("select count(*) from brands where parent_id = %s and is_serial = 1", (db_brand_id,))
        is_have_serial = c.fetchone()[0]
        print(is_have_serial, now_is_serial, now_is_model)
        if is_have_serial and (not now_is_serial and not now_is_model):
            if now_is_model or now_is_serial:
                inline_kb = await dynamic_keyboards.multiple_brands(c, find_id, parent_id=brand_id)
            else:
                inline_kb = await dynamic_keyboards.get_brands(c, find_id, is_find=1, parent_id=brand_id)
            await message.edit_text(text=f'<b>Выберите '
                                         f'{"тип" if category_id in (28,) else ("корпус" if category_id == -1 else ("серию" if now_is_serial or 1 else "модель"))}'
                                         f' 👇</b>',
                                    reply_markup=inline_kb)
        else:
            all_ads = await find_results(c, find_id)
            await message.edit_text(f'{await find_info.get_find_text(c, find_id, count_ads=len(all_ads))}',
                                    reply_markup=await dynamic_keyboards.edit_find_params(c, find_id,
                                                                                          count_ads=len(all_ads)))

    elif 'findAdSelectCategory' == start_data:
        if two_param:
            c.execute("select city_id from users where user_id = %s", (user_id,))
            city_id = c.fetchone()[0]
            c.execute("insert into finds (category_id, section_id, user_id, city_id) values (%s, %s, %s, %s)",
                      (one_param, two_param, user_id, city_id))
            conn.commit()
            find_id = c.lastrowid
            if int(one_param) == 6:
                inline_kb = await dynamic_keyboards.get_brands(c, find_id, is_find=1)
            else:
                inline_kb = await dynamic_keyboards.get_body_parts(c, find_id, is_find=1)
            await message.edit_text(text=f'<b>Выберите {"марку" if int(one_param) != 14 else "часть тела"} 👇</b>',
                                    reply_markup=inline_kb)
        elif int(one_param):
            await message.edit_text("<b>В каком разделе нужно найти объявление?</b> ⤵",
                                    reply_markup=await dynamic_keyboards.get_categories(c, one_param,
                                                                                        start_query=null_param))
        else:
            await message.edit_text("<b>В какой категории Вы бы хотели искать объявление?</b> ⤵",
                                    reply_markup=await dynamic_keyboards.get_categories(c, start_query=null_param))

    elif 'placeTimeNotify' == start_data:
        find_id = one_param
        c.execute("update finds set notify_days = %s where find_id = %s", (two_param, find_id))
        conn.commit()
        c.execute("select category_id from finds where find_id = %s", (find_id,))
        category_id = c.fetchone()[0]
        if category_id == 6:
            inline_kb = await dynamic_keyboards.get_brands(c, find_id, is_find=1)
        else:
            inline_kb = await dynamic_keyboards.get_body_parts(c, find_id, is_find=1)
        await message.edit_text(text=f'<b>Выберите {"марку" if int(one_param) != 14 else "часть тела"} 👇</b>',
                                reply_markup=inline_kb)

    elif 'selectClothesBrandPage' == start_data:
        await message.edit_reply_markup(reply_markup=await dynamic_keyboards.clothes_brands(c, one_param,
                                                                                            int(two_param),
                                                                                            page=int(three_param)))

    elif 'selectClothesTypesPage' == start_data:
        await message.edit_reply_markup(reply_markup=await dynamic_keyboards.closes_types(c, one_param,
                                                                                          is_type=int(two_param),
                                                                                          is_find=int(three_param),
                                                                                          page=int(four_param)))

    elif 'pauseNotify' == start_data:
        find_id = one_param
        c.execute("select is_active from finds where find_id = %s", (find_id,))
        is_active = c.fetchone()[0]
        c.execute("update finds set is_active = not is_active where find_id = %s", (find_id,))
        conn.commit()
        await callback_query.answer(
            "Ваше оповещение поставлено на паузу" if is_active else "Ваше оповещение снова в работе",
            show_alert=True)
        all_ads = await find_results(c, find_id)
        await message.edit_text(f"{await find_info.get_find_text(c, find_id, count_ads=len(all_ads))}",
                                reply_markup=await dynamic_keyboards.get_notify_menu(c, find_id))

    elif 'setNotification' == start_data:
        find_id = one_param
        all_ads = await find_results(c, find_id)
        if not all_ads and 0:
            await callback_query.answer("При заданных параметрах объявления найти не удастся. Попробуйте расширить "
                                        "параметры поиска",
                                        show_alert=True)
        else:
            await callback_query.answer("Оповещение создано ✅\n\n"
                                        "Остановить уведомления по оповещению Вы можете в меню -> уведомления",
                                        show_alert=True)
            c.execute("select balance from users where user_id = %s", (user_id,))
            balance = c.fetchone()[0]
            c.execute("select tariff_price from finds where find_id = %s", (find_id,))
            tariff_price = c.fetchone()[0]
            if balance >= tariff_price:
                c.execute("update users set balance = balance - %s where user_id = %s", (tariff_price, user_id,))
                c.execute("update finds set is_active = 1, is_paid = 1, "
                          "close_notifications = date_add(NOW(), interval notify_days day) "
                          "where find_id = %s", (find_id,))
                conn.commit()
                await message.edit_text(f"{await find_info.get_find_text(c, find_id, count_ads=len(all_ads))}",
                                        reply_markup=await dynamic_keyboards.get_notify_menu(c, find_id))
            else:
                await message.answer(f"⚠ <b>Недостаточно средств на балансе</b>\n\n"
                                     f"Необходимо {tariff_price}₽, но у Вас только {balance}₽",
                                     reply_markup=dynamic_keyboards.balance_menu())

    elif 'notifyAdSelectCategory' == start_data:
        if two_param:
            c.execute("select city_id from users where user_id = %s", (user_id,))
            city_id = c.fetchone()[0]
            c.execute("insert into finds (category_id, section_id, user_id, is_notify, city_id, close_notifications) "
                      "values (%s, %s, %s, 1, %s, DATE_ADD(NOW(), interval 7 day))",
                      (one_param, two_param, user_id, city_id))
            conn.commit()
            find_id = c.lastrowid
            inline_kb = await dynamic_keyboards.time_placing_notify(c, find_id)
            await message.edit_text(text=f'<b>Выберите срок размещения</b>',
                                    reply_markup=inline_kb)
        elif int(one_param):
            await message.edit_text("<b>В каком разделе будем отслеживать объявления?</b> ⤵",
                                    reply_markup=await dynamic_keyboards.get_categories(c, one_param,
                                                                                        start_query=null_param))
        else:
            await message.edit_text("<b>В какой категории Вы бы хотели отслеживать объявления?</b> ⤵",
                                    reply_markup=await dynamic_keyboards.get_categories(c, start_query=null_param))

    elif 'nextAdParam' == start_data:
        ad_id = int(one_param)
        old_param_id = two_param
        # c.execute("select param_id from param_options where option_id = %s", (old_param_id,))
        # old_param_id = c.fetchone()[0]
        if old_param_id == '6':
            await message.edit_text(f'<b>Выберите время размещения</b> 👇',
                                    reply_markup=await dynamic_keyboards.select_time_placing(c, ad_id, 0, 0, 1))
        else:
            await ad_params.get_step(c, message, ad_id, old_param_id)

    elif 'backAdParam' == start_data:
        ad_id = int(one_param)
        old_param_id = two_param
        old_param_id = '1' if str(old_param_id) == '0' else old_param_id
        await ad_params.get_step(c, message, ad_id, old_param_id)

    elif 'nextFindParam' == start_data:
        ad_id = int(one_param)
        old_param_id = two_param
        await ad_params.get_step(c, message, ad_id, old_param_id, is_find=1)

    elif 'search' == start_data:
        find_id = int(one_param)
        find_number = int(two_param)
        all_ads = await find_results(c, find_id)
        if all_ads:
            inline_kb = await dynamic_keyboards.get_ad_menu(c, all_ads[find_number], user_id, find_id=find_id,
                                                            count_pages=len(all_ads), page=find_number)
            ad_text = await ad_info.get_ad_text(c, all_ads[find_number], user_id)
            await message.edit_text(text=f'{ad_text}',
                                    reply_markup=inline_kb)

        else:
            await callback_query.answer("Объявлений по заданным параметрам не найдено. Попробуйте расширить "
                                        "параметры поиска", show_alert=True)

    elif 'favourites' == start_data:
        find_number = int(one_param)
        c.execute("select ad_id from favourites_ads where user_id = %s and "
                  "(select count(*) from ads where ads.ad_id = favourites_ads.ad_id)", (user_id,))
        all_ads = [x[0] for x in c.fetchall()]
        if all_ads:
            inline_kb = await dynamic_keyboards.get_ad_menu(c, all_ads[find_number], user_id, find_id=0,
                                                            count_pages=len(all_ads), page=find_number,
                                                            is_favourites=1)
            ad_text = await ad_info.get_ad_text(c, all_ads[find_number], user_id)
            await message.edit_text(text=f'{ad_text}',
                                    reply_markup=inline_kb)
        else:
            await callback_query.answer("Объявлений по заданным параметрам не найдено. Попробуйте расширить "
                                        "параметры поиска", show_alert=True)

    elif 'editFindOption' == start_data:
        find_id = int(one_param)
        param_id = two_param
        if param_id == 'price':
            # await CreateFind.first()
            # await state.update_data(object_id=find_id)
            # await state.update_data(param_id=param_id)
            if not three_param:
                await message.edit_text("Выберите подходящий диапазон цен (в рублях) 👇",
                                        reply_markup=await dynamic_keyboards.edit_find_price_limit(c, find_id))
            else:
                if int(three_param):
                    c.execute("update finds set price_limit_id = %s where find_id = %s", (three_param, find_id))
                    conn.commit()
                all_ads = await find_results(c, find_id)
                await message.edit_text(f'{await find_info.get_find_text(c, find_id, count_ads=len(all_ads))}',
                                        reply_markup=await dynamic_keyboards.edit_find_params(c, find_id,
                                                                                              count_ads=len(all_ads)))
        else:
            try:
                c.execute("select param_type, question_text from params where param_id = %s", (param_id,))
                param_type, param_question = c.fetchone()
                if param_type in ("int", "float"):
                    await CreateFind.first()
                    await state.update_data(object_id=find_id)
                    await state.update_data(param_id=param_id)
                    await message.edit_text(param_question)
                else:
                    await message.edit_text(param_question,
                                            reply_markup=await dynamic_keyboards.get_find_param_keyboard(c, param_id,
                                                                                                         find_id))
            except Exception as e:
                logging.info(e, exc_info=True)
                await callback_query.answer("Сначала необходимо выбрать серию или модель",
                                            show_alert=True)

    elif 'adWarning' == start_data:
        c.execute("update ads set is_warning = 1 where ad_id = %s", (one_param,))
        conn.commit()
        await callback_query.answer("Спасибо, Ваша жалоба отправлена администрации",
                                    show_alert=True)

    elif 'addFavourites' == start_data:
        c.execute("select count(*) from favourites_ads where ad_id = %s and user_id = %s", (one_param, user_id))
        is_favourite = c.fetchone()[0]
        if not is_favourite:
            c.execute("insert into favourites_ads (user_id, ad_id) values (%s, %s)", (user_id, one_param))
            conn.commit()
            await callback_query.answer("Объявление добавлено в избранное",
                                        show_alert=True)
        else:
            c.execute("delete from favourites_ads where user_id = %s and ad_id = %s", (user_id, one_param))
            conn.commit()
            await callback_query.answer("Объявление удалено из избранных",
                                        show_alert=True)
        if int(two_param):
            all_ads = await find_results(c, two_param)
            inline_kb = await dynamic_keyboards.get_ad_menu(c, one_param, user_id, find_id=two_param,
                                                            count_pages=len(all_ads), page=int(three_param))
        else:
            c.execute("select ad_id from favourites_ads where user_id = %s", (user_id,))
            all_ads = [x[0] for x in c.fetchall()]
            inline_kb = await dynamic_keyboards.get_ad_menu(c, one_param, user_id, find_id=two_param,
                                                            count_pages=len(all_ads), page=int(three_param),
                                                            is_favourites=1)
        await message.edit_reply_markup(reply_markup=inline_kb)

    elif 'backToFind' == start_data:
        find_id = one_param
        all_ads = await find_results(c, find_id)
        await message.edit_text(f"{await get_find_text(c, one_param, count_ads=len(all_ads))}",
                                reply_markup=await dynamic_keyboards.edit_find_params(c, one_param,
                                                                                      count_ads=len(all_ads)))

    elif 'publishAd' == start_data:
        ad_id = int(one_param)
        c.execute("select balance from users where user_id = %s", (user_id,))
        balance = c.fetchone()[0]
        c.execute("select tariff_price from ads where ad_id = %s", (ad_id,))
        tariff_price = c.fetchone()[0]
        if balance >= tariff_price:
            c.execute("update users set balance = balance - %s where user_id = %s", (tariff_price, user_id,))
            c.execute("update ads set is_paid = %s where ad_id = %s", (1, ad_id,))
            conn.commit()
            await callback_query.answer("Ваше объявление опубликовано, удалить его вы сможете в "
                                        "меню > профиль > мои объявления",
                                        show_alert=True)
            await message.edit_text(f"{await ad_info.get_ad_text(c, ad_id)}",
                                    reply_markup=await dynamic_keyboards.get_ad_menu(c, ad_id, user_id))
        else:
            await message.answer(f"⚠ <b>Недостаточно средств на балансе</b>\n\n"
                                 f"Необходимо {tariff_price}₽, но у Вас только {balance}₽",
                                 reply_markup=dynamic_keyboards.balance_menu())

    elif 'showAds' == start_data:
        page = int(one_param)
        result_text, inline_kb = await show_ads(c, page=page, user_id=user_id, is_my_ads=1)
        await message.edit_text(result_text,
                                reply_markup=inline_kb)

    elif 'returnToCreateAd' == start_data:
        ad_id = int(one_param)
        await state.update_data(object_id=ad_id)
        await CreateAd.price.set()
        await message.delete()
        await bot.send_message(user_id,
                               f'💰 Введите <b>стоимость</b> услуги или товара',
                               reply_markup=default_keyboards.ad_price_menu)

    elif 'placeTimeAd' == start_data:
        ad_id = int(one_param)
        place_days_period = int(two_param)
        old_param_id = int(three_param)
        c.execute("select balance from users where user_id = %s", (user_id,))
        balance = c.fetchone()[0]
        c.execute("select section_id, category_id from ads where ad_id = %s", (ad_id,))
        section_id, category_id = c.fetchone()
        c.execute("select tariff_first_price, tariff_second_price "
                  "from categories where category_id = %s", (section_id,))
        tariff_first_price, tariff_second_price = c.fetchone()
        tariff_price = tariff_first_price if place_days_period == 15 else tariff_second_price
        if balance >= tariff_price:
            c.execute("update ads set place_days_period = %s, tariff_price = %s where ad_id = %s",
                      (place_days_period, tariff_price, ad_id,))
            conn.commit()
            next_step = 0
            try:
                if category_id in (14,):
                    new_param_id = 3
                else:
                    new_param_id, old_param_id = await define_step.get_last_and_future(c, ad_id, old_param_id)
                print(new_param_id, old_param_id)
                inline_kb = await dynamic_keyboards.get_ad_param_keyboard(c, ad_id, new_param_id)
                c.execute("select question_text from params where param_id = %s", (new_param_id,))
                question_text = c.fetchone()[0]
                await message.edit_text(f'<b>{question_text}</b>',
                                        reply_markup=inline_kb)
            except:
                next_step = 1
            if next_step:
                await message.edit_text("<b>Выберите источник фото</b> 👇\n\n"
                                        "💡 <i>\"Наше фото\" - фото, загруженное из интернета</i>",
                                        reply_markup=await dynamic_keyboards.select_type_photo(c, ad_id,
                                                                                               old_param_id=6))
        else:
            await message.answer(f"⚠ <b>Недостаточно средств на балансе</b>\n\n"
                                 f"Необходимо {tariff_price}₽, но у Вас только {balance}₽",
                                 reply_markup=dynamic_keyboards.balance_menu())

    elif 'skipSearch' == start_data:
        await message.answer(f"<b>/{config.COMMANDS[0][0]}</b> - найти объявление\n"
                             f"<b>/{config.COMMANDS[1][0]}</b> - подать объявления\n"
                             f"<b>/{config.COMMANDS[2][0]}</b> - настроить оповещения\n"
                             f"<b>/{config.COMMANDS[3][0]}</b> - изменить город, баланс\n"
                             f"<b>/{config.COMMANDS[4][0]}</b> - задать вопрос",
                             reply_markup=get_user_menu(c, user_id))
        await message.delete()

    elif 'deleteNotify' == start_data:
        if two_param:
            c.execute("delete from finds where find_id = %s", (one_param,))
            c.execute("delete from find_brands where find_id = %s", (one_param,))
            c.execute("delete from find_options where find_id = %s", (one_param,))
            conn.commit()
            await callback_query.answer("Оповещение удалено ✅",
                                        show_alert=True)
            await message.delete()
            await state.finish()
            if int(two_param):
                await bot.delete_message(chat_id=user_id,
                                         message_id=two_param)
            await message.answer(f"<b>/{config.COMMANDS[0][0]}</b> - найти объявление\n"
                                 f"<b>/{config.COMMANDS[1][0]}</b> - подать объявления\n"
                                 f"<b>/{config.COMMANDS[2][0]}</b> - настроить оповещения\n"
                                 f"<b>/{config.COMMANDS[3][0]}</b> - изменить город, баланс\n"
                                 f"<b>/{config.COMMANDS[4][0]}</b> - задать вопрос",
                                 reply_markup=get_user_menu(c, user_id))
        else:
            await message.answer("⚠ <b>Вы действительно хотите удалить данное оповещение?</b>",
                                 reply_markup=dynamic_keyboards.delete_object(f'{query_data}_{message_id}'))

    elif 'resetAd' == start_data:
        if two_param:
            c.execute("delete from ads where ad_id = %s", (one_param,))
            c.execute("delete from ads_photos where ad_id = %s", (one_param,))
            c.execute("delete from ad_options where ad_id = %s", (one_param,))
            conn.commit()
            await callback_query.answer("Объявление удалено ✅",
                                        show_alert=True)
            await message.delete()
            await state.finish()
            if int(two_param):
                await bot.delete_message(chat_id=user_id,
                                         message_id=two_param)
            await message.answer(f"<b>/{config.COMMANDS[0][0]}</b> - найти объявление\n"
                                 f"<b>/{config.COMMANDS[1][0]}</b> - подать объявления\n"
                                 f"<b>/{config.COMMANDS[2][0]}</b> - настроить оповещения\n"
                                 f"<b>/{config.COMMANDS[3][0]}</b> - изменить город, баланс\n"
                                 f"<b>/{config.COMMANDS[4][0]}</b> - задать вопрос",
                                 reply_markup=get_user_menu(c, user_id))
        else:
            await message.answer("⚠ <b>Вы действительно хотите удалить данное объявление?</b>",
                                 reply_markup=dynamic_keyboards.delete_object(f'{query_data}_{message_id}'))

    elif 'deletePhotoAd' == start_data:
        if two_param:
            if int(two_param):
                c.execute("delete from ads_photos where photo_id = %s", (one_param,))
                conn.commit()
                await callback_query.answer("Фото удалено 🗑",
                                            show_alert=True)
                await message.delete()
            else:
                await message.edit_caption('Фото',
                                           reply_markup=dynamic_keyboards.delete_photo(f'{start_data}_{one_param}'))
                await callback_query.answer("Удаление отменено ✅",
                                            show_alert=True)
        else:
            await message.edit_caption("⚠ <b>Вы действительно хотите удалить фото?</b>",
                                       reply_markup=dynamic_keyboards.delete_object(f'{query_data}_{1}',
                                                                                    f'{query_data}_{0}'))

    elif 'selectPhotoType' == start_data:
        ad_id = int(one_param)
        c.execute("update ads set photo_type = %s where ad_id = %s", (two_param, ad_id,))
        conn.commit()
        await state.update_data(object_id=ad_id)
        if two_param == 'my':
            await CreateAd.first()
            await message.answer("📷 <b>Загрузите до 10 фото</b>",
                                 reply_markup=default_keyboards.back_reset_menu)
        else:
            await CreateAd.description.set()
            await message.answer(f'<b>Дополните объявление описанием</b>\n\n'
                                 f'💡 Не более 110 символов',
                                 reply_markup=default_keyboards.skip_menu)
        await message.delete()

    elif 'seeAdPhotos' == start_data:
        ad_photos = await ad_info.get_ad_photos(c, one_param)
        if not ad_photos[0]:
            try:
                c.execute("select brand_id from ads where ad_id = %s", (one_param,))
                brand_id = c.fetchone()[0]
                c.execute("select option_id from ad_options where ad_id = %s and param_id = 2", (one_param,))
                option_id = c.fetchone()[0]
                c.execute("select brand_param_id from brand_params "
                          "where brand_id = %s and option_id = %s and param_id = 2",
                          (brand_id, option_id,))
                color_id = c.fetchone()[0]
                c.execute("select photo_link from brands_photos where color_id = %s", (color_id,))
                all_photos_links = [x[0] for x in c.fetchall()]
                all_photos_links_group = MediaGroup(medias=[InputMedia(media=i) for i in all_photos_links])
                ad_photos = [all_photos_links, all_photos_links_group]
            except:
                ad_photos = [[]]
        if len(ad_photos[0]) > 1:
            message_info = await bot.send_media_group(user_id,
                                                      media=ad_photos[1])
            await message_info[0].reply("Нажмите, чтобы закончить просмотр фотоальбома 👇",
                                        reply_markup=await dynamic_keyboards.close_photos(message_info))
        elif ad_photos[0]:
            await message.answer_photo(ad_photos[0][0],
                                       reply_markup=await dynamic_keyboards.close_menu())
        else:
            await callback_query.answer("Фото не были добавлены",
                                        show_alert=True)

    elif 'editAdPhotos' == start_data:
        c.execute("select photo_id, photo_link from ads_photos where ad_id = %s limit 10", (one_param,))
        for one_photo in c.fetchall():
            send_message = await bot.send_photo(user_id,
                                                photo=one_photo[1],
                                                reply_markup=dynamic_keyboards.delete_photo(
                                                    f'deletePhotoAd_{one_photo[0]}'))
        await bot.send_message(user_id,
                               f'<b>Отправьте еще одно фото или нажмите '
                               f'кнопку [{default_buttons.button_continue.text}]</b>',
                               reply_markup=default_keyboards.load_photo_menu)

    elif 'stopAd' == start_data:
        ad_id = one_param
        c.execute("select is_pause from ads where ad_id = %s", (ad_id,))
        old_is_pause = c.fetchone()[0]
        await callback_query.answer(f"Теперь объявление "
                                    f"{'не показывается' if not old_is_pause else 'снова показывается'} в поиске",
                                    show_alert=True)
        c.execute("update ads set is_pause = abs(is_pause - 1) where ad_id = %s", (ad_id,))
        conn.commit()
        await message.edit_text(text=f"{await ad_info.get_ad_text(c, ad_id, user_id)}",
                                reply_markup=await dynamic_keyboards.get_ad_menu(c, ad_id, user_id))

    elif 'selectAdParamOption' == start_data:
        ad_id = int(one_param)
        param_id = int(two_param)
        option_id = int(three_param)
        # c.execute("select count(*) from ad_options where ad_id = %s and option_id = %s",
        #           (ad_id, option_id))
        # if not c.fetchone()[0]:
        #     c.execute("insert into ad_options (ad_id, option_id, param_id) values (%s, %s, %s)",
        #               (ad_id, option_id, param_id))
        #     conn.commit()
        await step_messages.send_step_message(c, conn, message, ad_id, param_id, option_id=option_id)
        # new_param_id, old_param_id = await define_step.get_last_and_future(c, ad_id, param_id)
        # if new_param_id == 6:
        #     c.execute("insert into ad_options (ad_id, option_id, param_id) values (%s, %s, %s)",
        #               (ad_id, option_id, param_id))
        #     conn.commit()
        #     # new_param_id, new_add_info = await get_future_step_by_param(c, ad_id, now_param_id=param_id)
        #     await message.edit_text(f'<b>Выберите тариф 👇</b>',
        #                             reply_markup=await select_time_placing(c, ad_id, new_param_id, old_param_id))
        # elif new_param_id == 'photo':
        #     pass
        # else:
        #     await send_step_message(c, conn, message, ad_id, param_id, option_id)

    elif 'listAdParamOptions' == start_data:
        ad_id = int(one_param)
        param_id = int(two_param)
        add_info = three_param
        page_id = int(0 if not four_param else four_param)
        await message.edit_reply_markup(await dynamic_keyboards.get_ad_param_keyboard(c, param_id, ad_id,
                                                                                      page=page_id))

    elif 'listBrands' == start_data:
        object_id = int(one_param)
        try:
            parent_id = int(two_param)
        except:
            parent_id = None
        is_find = int(three_param)
        page_id = int(0 if not four_param else four_param)
        await message.edit_reply_markup(await dynamic_keyboards.get_brands(c, object_id, is_find, parent_id, page_id))

    elif 'editFindSerial' == start_data:
        object_id = int(one_param)
        parent_id = int(two_param)
        page_id = int(0 if not three_param else three_param)
        await message.edit_reply_markup(await dynamic_keyboards.get_brands(c, object_id, 1, parent_id, page_id,
                                                                           is_edit=1))

    elif 'editFindModel' == start_data:
        object_id = int(one_param)
        parent_id = int(two_param)
        brand_id = int(0 if not three_param else three_param)
        page_id = int(0 if not four_param else four_param)
        if brand_id:
            c.execute("select count(*) from find_brands where find_id = %s and brand_id = %s", (object_id, brand_id))
            if c.fetchone()[0]:
                c.execute("delete from find_brands where find_id = %s and brand_id = %s", (object_id, brand_id))
            else:
                c.execute("insert into find_brands (find_id, brand_id) values (%s, %s)", (object_id, brand_id))
            conn.commit()
        await message.edit_reply_markup(await dynamic_keyboards.multiple_brands(c, object_id, parent_id=parent_id,
                                                                                page=page_id))

    elif 'selectFindParamOption' == start_data:
        find_id = int(one_param)
        param_id = int(two_param)
        option_id = int(three_param)
        all_param_options = []
        c.execute("select brand_id, model_id, serial_id, section_id from finds where find_id = %s", (find_id,))
        old_brand_id, model_id, serial_id, section_id = c.fetchone()
        c.execute("select brand_id from find_brands where find_id = %s", (find_id,))
        selected_brands = [x[0] for x in c.fetchall()] + [old_brand_id, model_id, serial_id]
        for brand_id in selected_brands:
            c.execute("select option_id "
                      "from brand_params "
                      "where param_id = %s and brand_id = %s",
                      (param_id, brand_id))
            param_options_brand = [x[0] for x in c.fetchall()]
            all_param_options += param_options_brand
        c.execute("select section_id from finds where find_id = %s", (find_id,))
        if all_param_options[0] == 0:
            c.execute("select option_id from options where param_id = %s", (param_id,))
            all_param_options = [x[0] for x in c.fetchall()]
        all_param_options = list(set(all_param_options))
        c.execute("select param_type from params where param_id = %s", (param_id,))
        param_type = c.fetchone()[0]
        c.execute("select option_id from find_options where param_id = %s and find_id = %s", (param_id, find_id))
        all_find_param_options = [x[0] for x in c.fetchall()]
        if param_type == 'list' and 0:
            c.execute("delete from find_options where param_id = %s and find_id = %s", (param_id, find_id))
            if option_id not in all_find_param_options:
                c.execute("insert into find_options (find_id, option_id, param_id) "
                          "values (%s, %s, %s)", (find_id, option_id, param_id))
            conn.commit()
            all_ads = await find_results(c, find_id)
            await message.edit_text(f"{await get_find_text(c, find_id, count_ads=len(all_ads))}",
                                    reply_markup=await dynamic_keyboards.edit_find_params(c, find_id,
                                                                                          count_ads=len(all_ads)))
        else:
            print(option_id, all_param_options)
            if option_id:
                if option_id in all_find_param_options:
                    c.execute("delete from find_options where option_id = %s and find_id = %s", (option_id, find_id))
                else:
                    c.execute("insert into find_options (find_id, option_id, param_id) "
                              "values (%s, %s, %s)", (find_id, option_id, param_id))
            else:
                for k in all_param_options:
                    print(k)
                    c.execute("select count(*) from find_options where find_id = %s and option_id = %s",
                              (find_id, k))
                    if not c.fetchone()[0]:
                        if set(all_param_options) != set(all_find_param_options):
                            c.execute("insert into find_options (find_id, option_id, param_id) "
                                      "values (%s, %s, %s)", (find_id, k, param_id))
                    else:
                        if set(all_param_options) == set(all_find_param_options):
                            c.execute("delete from find_options where option_id = %s and find_id = %s",
                                      (k, find_id))
            conn.commit()
            await message.edit_reply_markup(await dynamic_keyboards.get_find_param_keyboard(c, param_id, find_id))

    elif 'addParamsAllModels' == start_data:
        brand_id = one_param
        await message.answer("Выберите параметр",
                             reply_markup=await dynamic_keyboards.options_for_admin(c, brand_id))

    elif 'addInfo' == start_data:
        if not two_param:
            if one_param == 'params':
                await message.edit_text(f'Выберите параметр',
                                        reply_markup=await dynamic_keyboards.params_for_admin(c))
            elif one_param == 'brands':
                await message.edit_text(f'Выберите бренд',
                                        reply_markup=await dynamic_keyboards.brands_for_admin(c))
        else:
            if one_param == 'params':
                await state.update_data(info_type=one_param)
                await state.update_data(param_id=two_param)
                await AddInformation.first()
                await message.answer("Отправьте список новых опций в столбик")
            elif one_param == 'brands':
                await message.edit_text(f'Выберите бренд',
                                        reply_markup=await dynamic_keyboards.brands_for_admin(c, parent_id=two_param))
            elif one_param == 'options':
                await state.update_data(info_type=one_param)
                await state.update_data(param_id=two_param)
                await state.update_data(brand_id=three_param)
                await AddInformation.first()
                await message.reply("Отправьте в столбик опции к бренду")

    elif 'addBrands' == start_data:
        await state.update_data(info_type='brands')
        await state.update_data(brand_id=one_param)
        await AddInformation.first()
        await message.answer("Отправьте список новых брендов в столбик")

    elif 'addParamsModels' == start_data:
        await state.update_data(info_type='brands_params')
        await state.update_data(brand_id=one_param)
        await AddInformation.first()
        await message.answer("Отправьте список формата:\n"
                             "Модель    Параметры")

    elif 'depositMoney' == start_data:
        if one_param:
            money_value = int(one_param)
            pay_link = await create_payment(payment_value=money_value, user_id=user_id)
            print(pay_link)
            c.execute("insert into payments (user_id, payment_amount, system_id) values (%s, %s, %s)",
                      (user_id, money_value, pay_link['id']))
            conn.commit()
            await state.finish()
            await message.edit_text(f"⏱ <b>Средства будут зачислены в течение 5 минут после оплаты\n\n"
                                    f"👇 Ссылка на оплату</b>\n\n"
                                    f"{pay_link['confirmation']['confirmation_url']}")
        else:
            await message.answer("Выберите сумму пополнения",
                                 reply_markup=await dynamic_keyboards.deposit_money())

    elif 'selectCityType' == start_data:
        await state.finish()
        await SetCity.first()
        await state.update_data(city_type=one_param)
        await message.answer(f"Нажмите на кнопку ниже и начните вводить "
                             f"{'край' if one_param == 'region' else 'область'}",
                             reply_markup=await dynamic_keyboards.find_city(one_param))

    elif 'getSelectCityMethods' == start_data:
        c.execute("update users set city_id = NULL where user_id = %s", (user_id,))
        conn.commit()
        await message.delete()
        await message.answer("🗺 Как будем определять регион поиска/размещения объявлений?",
                             reply_markup=get_user_menu(c, user_id))

    elif 'showCities' == start_data:
        c.execute("select latitude, longitude from users where user_id = %s", (user_id,))
        latitude, longitude = c.fetchone()
        await message.edit_reply_markup(reply_markup=await nearest_towns.get_inline_kb(c, user_id,
                                                                                       page=int(one_param),
                                                                                       latitude=latitude,
                                                                                       longitude=longitude,
                                                                                       by_distance=int(four_param)))

    elif 'selectCity' == start_data:
        city_id = one_param
        page = int(two_param)
        c.execute("select latitude, longitude from users where user_id = %s", (user_id,))
        latitude, longitude = c.fetchone()
        c.execute("update users set city_id = %s where user_id = %s", (city_id, user_id))
        conn.commit()
        c.execute("select city_name from all_cities where city_id = %s", (city_id,))
        city_name = c.fetchone()[0]
        await message.edit_text(text=f'<b>Вы выбрали:</b> {city_name}\n\n'
                                     f'<b>Выберите другой город или продолжите заполнение анкеты</b> ⤵',
                                reply_markup=await nearest_towns.get_inline_kb(c, user_id,
                                                                               page=page,
                                                                               latitude=latitude,
                                                                               longitude=longitude))

    elif 'confirmSelectedCity' == start_data:
        await callback_query.answer("Город выбран ✅\n\n"
                                    "Теперь при просмотре объявления, установке оповещения или подаче объявления "
                                    "будет указываться этот город.\n\n"
                                    "Изменить город можно в разделе ПРОФИЛЬ",
                                    show_alert=True)
        c.execute("select bonus_value, is_get_bonus from users where user_id = %s", (user_id,))
        bonus_value, is_get_bonus = c.fetchone()
        if not is_get_bonus:
            c.execute("update users set balance = balance + %s, is_get_bonus = 1 "
                      "where user_id = %s", (bonus_value, user_id))
            conn.commit()
            if bonus_value:
                await message.answer(f"💰 <b>Вы получили бонус! {bonus_value} РУБ уже на Вашем счету!</b>")
        await asyncio.sleep(2)
        await message.delete()
        await message.answer("Регистрация успешно пройдена ✅\n\n"
                             "Теперь ознакомьтесь с кратким гайдом и попробуйте подать или найти объявления 👇")
        await message.answer(f"<b>/{config.COMMANDS[0][0]}</b> - найти объявление\n"
                             f"<b>/{config.COMMANDS[1][0]}</b> - подать объявления\n"
                             f"<b>/{config.COMMANDS[2][0]}</b> - настроить оповещения\n"
                             f"<b>/{config.COMMANDS[3][0]}</b> - изменить город, баланс\n"
                             f"<b>/{config.COMMANDS[4][0]}</b> - задать вопрос",
                             reply_markup=get_user_menu(c, user_id))

    await callback_query.answer()
    c.close()
    conn.close()
