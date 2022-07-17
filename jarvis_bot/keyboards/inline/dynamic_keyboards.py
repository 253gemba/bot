import math
from typing import List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from data import config
from loader import bot


def delete_object(query, reject_query='hide'):
    inline_kb = InlineKeyboardMarkup(row_width=2)
    inline_kb.insert(InlineKeyboardButton(text=f'Удалить',
                                          callback_data=f'{query}_1'))
    if reject_query:
        inline_kb.insert(InlineKeyboardButton(text=f'Отмена',
                                              callback_data=reject_query))
    return inline_kb


def delete_photo(query):
    inline_kb = InlineKeyboardMarkup(row_width=2)
    inline_kb.insert(InlineKeyboardButton(text=f'Удалить',
                                          callback_data=f'{query}'))
    return inline_kb


async def sub_on_channel():
    channel_url = await bot.export_chat_invite_link(config.CHECK_SUB_CHANNEL_ID)
    inline_kb = InlineKeyboardMarkup(row_width=2)
    inline_kb.row(InlineKeyboardButton(text=f'▶ Подписаться',
                                       url=channel_url))
    inline_kb.row(InlineKeyboardButton(text=f'✔ Проверить подписку',
                                       callback_data=f'checkSub'))
    return inline_kb


async def select_time_placing(c, ad_id, next_param_id, old_param_id, is_show_categories=0):
    # old_param_id, _ = await get_last_step(c, ad_id, now_param_id=new_param_id)
    c.execute("select section_id, category_id, serial_id from ads where ad_id = %s", (ad_id,))
    section_id, category_id, serial_id = c.fetchone()
    c.execute("select tariff_first_price, tariff_second_price "
              "from categories where category_id = %s", (section_id,))
    tariff_first_price, tariff_second_price = c.fetchone()
    inline_kb = InlineKeyboardMarkup(row_width=2)
    inline_kb.row(InlineKeyboardButton(text=f'15 дней = {tariff_first_price}₽',
                                       callback_data=f'placeTimeAd_{ad_id}_15_{next_param_id}'))
    inline_kb.row(InlineKeyboardButton(text=f'30 дней - {tariff_second_price}₽',
                                       callback_data=f'placeTimeAd_{ad_id}_30_{next_param_id}'))
    if is_show_categories or not old_param_id:
        if section_id not in (19,):
            back_button = f'createAdSelectCategory_{category_id}_{section_id}'
        else:
            back_button = f'selectBrandAd_{ad_id}_{serial_id}'
    else:
        back_button = f'nextAdParam_{ad_id}_{old_param_id}'
    inline_kb.row(InlineKeyboardButton(text=f'↩ Назад',
                                       callback_data=back_button))
    inline_kb.insert(InlineKeyboardButton(text=f'🔄 Сбросить объявление',
                                          callback_data=f'resetAd_{ad_id}'))
    return inline_kb


async def closes_time_placing(c, ad_id, is_find=0):
    if is_find:
        c.execute("select section_id from finds where find_id = %s", (ad_id,))
        section_id = c.fetchone()[0]
        c.execute("select tariff_notify_first, tariff_notify_second "
                  "from categories where category_id = %s", (section_id,))
        tariff_first_price, tariff_second_price = c.fetchone()
    else:
        c.execute("select section_id from ads where ad_id = %s", (ad_id,))
        section_id = c.fetchone()[0]
        c.execute("select tariff_first_price, tariff_second_price "
                  "from categories where category_id = %s", (section_id,))
        tariff_first_price, tariff_second_price = c.fetchone()
    inline_kb = InlineKeyboardMarkup(row_width=2)
    inline_kb.row(InlineKeyboardButton(text=f'15 дней = {tariff_first_price}₽',
                                       callback_data=f'placeTime_{ad_id}_15_{is_find}'))
    inline_kb.row(InlineKeyboardButton(text=f'30 дней - {tariff_second_price}₽',
                                       callback_data=f'placeTime_{ad_id}_30_{is_find}'))
    inline_kb.row(InlineKeyboardButton(text=f'↩ Назад',
                                       callback_data=f'nextAdParam_{ad_id}_{is_find}'))
    inline_kb.insert(InlineKeyboardButton(text=f'🔄 Сбросить объявление',
                                          callback_data=f'resetAd_{ad_id}'))
    return inline_kb


async def time_placing_notify(c, find_id):
    c.execute("select category_id, section_id from finds where find_id = %s", (find_id,))
    category_id, section_id = c.fetchone()
    c.execute("select tariff_notify_first, tariff_notify_second "
              "from categories where category_id = %s", (section_id,))
    tariff_first_price, tariff_second_price = c.fetchone()
    inline_kb = InlineKeyboardMarkup(row_width=2)
    inline_kb.row(InlineKeyboardButton(text=f'15 дней = {tariff_first_price}₽',
                                       callback_data=f'placeTimeNotify_{find_id}_15'))
    inline_kb.row(InlineKeyboardButton(text=f'30 дней - {tariff_second_price}₽',
                                       callback_data=f'placeTimeNotify_{find_id}_30'))
    inline_kb.row(InlineKeyboardButton(text=f'↩ Назад',
                                       callback_data=f'notifyAdSelectCategory_{category_id}'))
    inline_kb.insert(InlineKeyboardButton(text=f'🔄 Сбросить отслеживание',
                                          callback_data=f'skipSearch_{find_id}'))
    return inline_kb


async def select_type_photo(c, ad_id, old_param_id=None):
    # if not old_param_id:
    #     old_param_id, _ = await get_last_step(c, ad_id, now_param_id=now_param_id)
    c.execute("select section_id, brand_id from ads where ad_id = %s", (ad_id,))
    section_id, brand_id = c.fetchone()
    inline_kb = InlineKeyboardMarkup(row_width=2)
    inline_kb.row(InlineKeyboardButton(text=f'Свое фото',
                                       callback_data=f'selectPhotoType_{ad_id}_my'))
    if section_id not in (18, 28):
        if section_id in (17,) and brand_id not in (1896, 1914, 1915, 1916) or section_id != 17:
            inline_kb.row(InlineKeyboardButton(text=f'Наше фото',
                                               callback_data=f'selectPhotoType_{ad_id}_our'))
    inline_kb.row(InlineKeyboardButton(text=f'↩ Назад',
                                       callback_data=f'nextAdParam_{ad_id}_{old_param_id}'))
    inline_kb.insert(InlineKeyboardButton(text=f'🔄 Сбросить объявление',
                                          callback_data=f'resetAd_{ad_id}'))
    return inline_kb


async def get_categories(c, parent_id=0, start_query='createAdSelectCategory'):
    inline_kb = InlineKeyboardMarkup(row_width=2)
    c.execute("select category_id, category_name from categories "
              "where IF(%s, parent_id = %s, parent_id is NULL)", (parent_id, parent_id))
    db_categories = c.fetchall()
    for one_category in db_categories:
        category_id, category_name = one_category
        if parent_id:
            category_id = f'{parent_id}_{category_id}'
        inline_kb.insert(InlineKeyboardButton(text=f'{category_name}',
                                              callback_data=f'{start_query}_{category_id}'))
    if parent_id:
        c.execute("select parent_id from categories where category_id = %s", (parent_id,))
        try:
            old_category = c.fetchone()[0]
            old_category = 0 if not old_category else old_category
        except:
            old_category = 0
        inline_kb.row(InlineKeyboardButton(text=f'🔙 назад',
                                           callback_data=f'{start_query}_{old_category}'))
    return inline_kb


async def find_city(find_type='city'):
    inline_kb = InlineKeyboardMarkup(row_width=2)
    inline_kb.insert(InlineKeyboardButton(
        text=f'Найти {"край" if find_type == "region" else ("область" if find_type == "area" else "город")}',
        switch_inline_query_current_chat=f''))
    return inline_kb


async def add_type():
    inline_kb = InlineKeyboardMarkup(row_width=2)
    inline_kb.insert(InlineKeyboardButton(text=f'Параметры',
                                          callback_data=f'addInfo_params'))
    inline_kb.insert(InlineKeyboardButton(text=f'Бренды',
                                          callback_data=f'addInfo_brands'))
    return inline_kb


async def params_for_admin(c):
    inline_kb = InlineKeyboardMarkup(row_width=2)
    c.execute("select param_id, param_name from params")
    for param_id, param_name in c.fetchall():
        inline_kb.insert(InlineKeyboardButton(text=f'{param_name}',
                                              callback_data=f'addInfo_params_{param_id}'))
    return inline_kb


async def options_for_admin(c, brand_id):
    inline_kb = InlineKeyboardMarkup(row_width=2)
    c.execute("select param_id, param_name from params")
    for param_id, param_name in c.fetchall():
        inline_kb.insert(InlineKeyboardButton(text=f'{param_name}',
                                              callback_data=f'addInfo_options_{param_id}_{brand_id}'))
    return inline_kb


async def brands_for_admin(c, parent_id=None):
    inline_kb = InlineKeyboardMarkup(row_width=2)
    if not parent_id:
        c.execute("select category_id from brands group by category_id")
        all_categories = list(set([x[0] for x in c.fetchall()]))
        for one_category in all_categories:
            try:
                c.execute("select category_name from categories where category_id = %s", (one_category,))
                category_name = c.fetchone()[0]
                inline_kb.row(InlineKeyboardButton(text=f'👇 {category_name} 👇',
                                                   callback_data=f' '))
                inline_kb.row()
                c.execute("select brand_id, brand_name from brands "
                          "where IF(%s, parent_id = %s, parent_id is NULL) and category_id = %s",
                          (parent_id, parent_id, one_category))
                for brand_id, brand_name in c.fetchall():
                    inline_kb.insert(InlineKeyboardButton(text=f'{brand_name}',
                                                          callback_data=f'addInfo_brands_{brand_id}'))
            except:
                pass
    else:
        c.execute("select brand_id, brand_name from brands where IF(%s, parent_id = %s, parent_id is NULL)",
                  (parent_id, parent_id))
        for brand_id, brand_name in c.fetchall():
            inline_kb.insert(InlineKeyboardButton(text=f'{brand_name}',
                                                  callback_data=f'addInfo_brands_{brand_id}'))
    if parent_id:
        inline_kb.insert(InlineKeyboardButton(text=f'➕ Добавить сюда',
                                              callback_data=f'addBrands_{parent_id}'))
        inline_kb.insert(InlineKeyboardButton(text=f'➕ Параметры моделей',
                                              callback_data=f'addParamsModels_{parent_id}'))
        inline_kb.insert(InlineKeyboardButton(text=f'➕ Все параметры',
                                              callback_data=f'addParamsAllModels_{parent_id}'))
    return inline_kb


async def deposit_money():
    inline_kb = InlineKeyboardMarkup(row_width=2)
    all_prices = [20, 40, 60, 80, 100]
    for one_price in all_prices:
        inline_kb.insert(InlineKeyboardButton(text=f'{one_price}',
                                              callback_data=f'depositMoney_{one_price}'))
    return inline_kb


async def area_or_region():
    inline_kb = InlineKeyboardMarkup(row_width=1)
    inline_kb.insert(InlineKeyboardButton(text=f'Выбрать край',
                                          callback_data=f'selectCityType_region'))
    inline_kb.insert(InlineKeyboardButton(text=f'Выбрать область',
                                          callback_data=f'selectCityType_area'))
    return inline_kb


async def edit_notifications():
    inline_kb = InlineKeyboardMarkup(row_width=1)
    inline_kb.insert(InlineKeyboardButton(text=f'Отключить оповещения',
                                          callback_data=f'editNotification'))
    inline_kb.insert(InlineKeyboardButton(text=f'Выбрать область',
                                          callback_data=f'selectCityType_area'))
    return inline_kb


async def close_photos(message: List[Message]):
    inline_kb = InlineKeyboardMarkup(row_width=1)
    inline_kb.insert(InlineKeyboardButton(text=f'Закрыть фотоальбом ✖',
                                          callback_data=f'hide_{"_".join([str(x.message_id) for x in message])}'))
    return inline_kb


async def close_menu():
    inline_kb = InlineKeyboardMarkup(row_width=1)
    inline_kb.insert(InlineKeyboardButton(text=f'Скрыть сообщение ✖',
                                          callback_data=f'hide'))
    return inline_kb


async def get_ad_param_keyboard(c, ad_id=0, now_param_id=0, page=0, old_param_id=0):
    c.execute("select last_brand_id, category_id, section_id, model_id from ads where ad_id = %s", (ad_id,))
    last_brand_id, category_id, section_id, model_id = c.fetchone()
    inline_kb = InlineKeyboardMarkup(row_width=2)
    c.execute("select option_id, (select option_name from options where options.option_id = brand_params.option_id), "
              "param_position "
              "from brand_params "
              "where param_id = %s and brand_id = %s",
              (now_param_id, last_brand_id))
    param_options = c.fetchall()
    c.execute("select option_id from ad_options where ad_id = %s and param_id = %s", (ad_id, now_param_id))
    ad_options = [x[0] for x in c.fetchall()]
    offset = 10
    offset_param_options = param_options[page * offset:(page + 1) * offset]
    c.execute("select option_id from options where param_id = %s", (now_param_id,))
    all_param_options = [x[0] for x in c.fetchall()]
    selected_all = set(all_param_options) == set(ad_options)
    if offset_param_options[0][0] == 0:
        c.execute("select option_id, option_name, 1 from options where param_id = %s", (now_param_id,))
        offset_param_options = c.fetchall()
    for one_param in offset_param_options:
        option_id, option_name, _ = one_param
        button = InlineKeyboardButton(text=f'{"✅" if option_id in ad_options else "⬜"} {option_name}',
                                      callback_data=f'selectAdParamOption_{ad_id}_{now_param_id}_{option_id}')
        if offset_param_options.index(one_param):
            inline_kb.insert(button)
        else:
            inline_kb.row(button)
    c.execute("select param_type from params where param_id = %s", (now_param_id,))
    param_type = c.fetchone()[0]
    if param_type in ('multilist',):
        inline_kb.row(InlineKeyboardButton(text=f'{"✅" if selected_all else "⬜"} Всё сразу',
                                           callback_data=f'selectAdParamOption_{ad_id}_'
                                                         f'{now_param_id}_{0}'))
    inline_kb.row(InlineKeyboardButton(text=f'<<' if page > 0 else '',
                                       callback_data=f'listAdParamOptions_{ad_id}_{now_param_id}_{page - 1}'),
                  InlineKeyboardButton(text=f'>>' if page + 1 < math.ceil(len(param_options) / offset) else '',
                                       callback_data=f'listAdParamOptions_{ad_id}_{now_param_id}_{page + 1}'))
    print(f'old_param_id: {now_param_id}')
    if param_options[0][2] > 1:
        if old_param_id:
            back_query = f'backAdParam_{ad_id}_{old_param_id}'
        else:
            back_query = f'nextAdParam_{ad_id}_{6}'
    else:
        c.execute("select last_brand_id from ads where ad_id = %s", (ad_id,))
        last_brand_id = c.fetchone()[0]
        c.execute("select parent_id from brands where brand_id = %s", (last_brand_id,))
        parent_last_brand_id = c.fetchone()[0]
        if parent_last_brand_id:
            back_query = f'selectBrandAd_{ad_id}_{parent_last_brand_id}'
        else:
            back_query = f'createAdSelectCategory_{category_id}_{section_id}'
    inline_kb.row(InlineKeyboardButton(text=f'⏩ Продолжить' if ad_options else '',
                                       callback_data=f'backAdParam_{ad_id}_{now_param_id}'))
    inline_kb.row(InlineKeyboardButton(text=f'↩ Назад',
                                       callback_data=back_query))
    inline_kb.insert(InlineKeyboardButton(text=f'🔄 Сбросить объявление',
                                          callback_data=f'resetAd_{ad_id}'))
    return inline_kb


async def edit_find_params(c, find_id, count_ads=0):
    inline_kb = InlineKeyboardMarkup(row_width=2)
    c.execute("select section_id, category_id, is_notify, brand_id, serial_id, model_id, last_brand_id "
              "from finds where find_id = %s", (find_id,))
    section_id, category_id, is_notify, brand_id, serial_id, model_id, last_brand_id = c.fetchone()
    all_find_params = []
    c.execute("select brand_id from find_brands where find_id = %s", (find_id,))
    for selected_brand in c.fetchall() + [(serial_id,), (brand_id,)]:
        print(selected_brand)
        c.execute("select param_id, (select param_name from params where params.param_id = brand_params.param_id) "
                  "from brand_params where category_id = %s and brand_id = %s group by param_id",
                  (section_id, selected_brand[0]))
        db_brands = c.fetchall()
        all_find_params += db_brands
    # if section_id == 13:
    #     all_find_params = [(18, 'Разъем')]
    all_find_params = list(set(all_find_params))
    if category_id == 6:
        if serial_id and 0:
            inline_kb.insert(InlineKeyboardButton(text=f'Серия',
                                                  callback_data=f'editFindSerial_{find_id}_{brand_id}'))
        c.execute("select count(*) from brands where parent_id = %s", (serial_id if serial_id else brand_id,))
        if c.fetchone()[0]:
            inline_kb.insert(InlineKeyboardButton(text=f'Выбрать {"модель" if section_id != 19 else "корпус"}',
                                                  callback_data=f'editFindModel_{find_id}_{serial_id if serial_id else brand_id}'))
    inline_kb.row()
    for param_id, param_name in all_find_params:
        if param_id not in (6, 17, 25):
            inline_kb.insert(InlineKeyboardButton(text=f'{param_name}',
                                                  callback_data=f'editFindOption_{find_id}_{param_id}'))
    if category_id == 6:
        inline_kb.insert(InlineKeyboardButton(text=f'💰 Диапазон цены',
                                              callback_data=f'editFindOption_{find_id}_price'))
    # if count_ads:
    inline_kb.row(InlineKeyboardButton(text=f'🔎 Начать поиск' if not is_notify else '🔔 Начать отслеживание',
                                       callback_data=f'search_{find_id}_0' if not is_notify else f'setNotification_{find_id}'))
    inline_kb.row(InlineKeyboardButton(text=f'↩ Назад',
                                       callback_data=f'selectBrandFind_{find_id}_{brand_id}_1' if 0 else f'findAdSelectCategory_{category_id}_{section_id}'))
    inline_kb.row(InlineKeyboardButton(text=f'✖ Завершить поиск',
                                       callback_data=f'skipSearch'))
    return inline_kb


async def edit_find_price_limit(c, find_id):
    inline_kb = InlineKeyboardMarkup(row_width=1)
    c.execute("select section_id from finds where find_id = %s", (find_id,))
    section_id = c.fetchone()[0]
    c.execute("select price_limit_id, start_price, finish_price "
              "from category_price_limits where category_id = %s",
              (section_id,))
    for price_limit_id, start_price, finish_price in c.fetchall():
        if not start_price:
            button_text = f'До {finish_price}'
        elif not finish_price:
            button_text = f'Более {start_price}'
        else:
            button_text = f'От {start_price} до {finish_price}'
        inline_kb.insert(InlineKeyboardButton(text=f'{button_text}',
                                              callback_data=f'editFindOption_{find_id}_price_{price_limit_id}'))
    inline_kb.row(InlineKeyboardButton(text=f'↩ Назад',
                                       callback_data=f'editFindOption_{find_id}_price_{0}'))
    return inline_kb


async def get_brand_type(c, object_id, is_find=0):
    if not is_find:
        c.execute("select category_id, section_id, brand_id from ads where ad_id = %s", (object_id,))
    else:
        c.execute("select category_id, section_id, brand_id from finds where find_id = %s", (object_id,))
    category_id, section_id, brand_id = c.fetchone()
    inline_kb = InlineKeyboardMarkup(row_width=2)
    inline_kb.insert(InlineKeyboardButton(text=f'Брендовая',
                                          callback_data=f'typeBrandClothes_{object_id}_{is_find}'))
    inline_kb.insert(InlineKeyboardButton(text=f'Не брендовая',
                                          callback_data=f'selectPartClothes_{object_id}_{is_find}'))
    inline_kb.row(InlineKeyboardButton(text=f'↩ Назад',
                                       callback_data=f'createAdSelectCategory_{category_id}_{section_id}'))
    return inline_kb


async def get_size_format(c, object_id, is_find=0):
    if not is_find:
        c.execute("select category_id, section_id, closes_body_part, closes_type from ads "
                  "where ad_id = %s", (object_id,))
    else:
        c.execute("select category_id, section_id, closes_body_part, closes_type from finds "
                  "where find_id = %s", (object_id,))
    category_id, section_id, closes_body_part, closes_type = c.fetchone()
    inline_kb = InlineKeyboardMarkup(row_width=2)
    if closes_body_part not in ('shoes',):
        inline_kb.insert(InlineKeyboardButton(text=f'Размер цифрами',
                                              callback_data=f'setSizeType_{object_id}_numeric_{is_find}'))
        inline_kb.insert(InlineKeyboardButton(text=f'Размер буквами',
                                              callback_data=f'setSizeType_{object_id}_alpha_{is_find}'))
    else:
        inline_kb.insert(InlineKeyboardButton(text=f'Размер Европа',
                                              callback_data=f'setSizeType_{object_id}_eu_{is_find}'))
        inline_kb.insert(InlineKeyboardButton(text=f'Размер США',
                                              callback_data=f'setSizeType_{object_id}_usa_{is_find}'))
    inline_kb.row(InlineKeyboardButton(text=f'↩ Назад',
                                       callback_data=f'selectPartClothes_{object_id}_{is_find}'))
    return inline_kb


async def get_sizes(c, object_id, is_find=0, param_id=0, page=0):
    inline_kb = InlineKeyboardMarkup(row_width=2)
    if is_find:
        c.execute("select option_id from find_options where param_id = %s and find_id = %s",
                  (param_id, object_id))
    else:
        c.execute("select option_id from ad_options where param_id = %s and ad_id = %s",
                  (param_id, object_id))
    ad_options = [x[0] for x in c.fetchall()]
    c.execute("select option_id, option_name from options where param_id = %s", (param_id,))
    offset = 10
    all_sizes = c.fetchall()
    offset_param_options = all_sizes[page*offset:(page + 1) * offset]
    for one_param in offset_param_options:
        option_id, option_name = one_param
        button = InlineKeyboardButton(text=f'{"✅" if option_id in ad_options else "⬜"} {option_name}',
                                      callback_data=f'selectClosesParamOption_{object_id}_{param_id}_{option_id}_{is_find}')
        if offset_param_options.index(one_param):
            inline_kb.insert(button)
        else:
            inline_kb.row(button)
    inline_kb.row(InlineKeyboardButton(text=f'<<' if page > 0 else '',
                                       callback_data=f'selectClosesParamOptionPage_{object_id}_'
                                                     f'{param_id}_{is_find}_{page - 1}'),
                  InlineKeyboardButton(text=f'>>' if page + 1 < math.ceil(len(all_sizes) / offset) else '',
                                       callback_data=f'selectClosesParamOptionPage_{object_id}_'
                                                     f'{param_id}_{is_find}_{page + 1}'))
    if ad_options:
        inline_kb.row(InlineKeyboardButton(text=f'Следующий шаг ⏩',
                                           callback_data=f'backToFind_{object_id}'))
    inline_kb.row(InlineKeyboardButton(text=f'↩ Назад',
                                       callback_data=f'selectPartClothes_{object_id}_{is_find}'))
    return inline_kb


async def get_body_parts(c, object_id, is_find=0):
    if not is_find:
        c.execute("select category_id, section_id, brand_id from ads where ad_id = %s", (object_id,))
    else:
        c.execute("select category_id, section_id, brand_id from finds where find_id = %s", (object_id,))
    category_id, section_id, brand_id = c.fetchone()
    inline_kb = InlineKeyboardMarkup(row_width=2)
    inline_kb.insert(InlineKeyboardButton(text=f'Верхняя часть',
                                          callback_data=f'setBodyPart_{object_id}_up_{is_find}'))
    inline_kb.insert(InlineKeyboardButton(text=f'Нижняя часть',
                                          callback_data=f'setBodyPart_{object_id}_down_{is_find}'))
    inline_kb.insert(InlineKeyboardButton(text=f'Обувь',
                                          callback_data=f'setBodyPart_{object_id}_shoes_{is_find}'))
    inline_kb.row(InlineKeyboardButton(text=f'↩ Назад',
                                       callback_data=f'createAdSelectCategory_{category_id}'))
    return inline_kb


async def closes_types(c, object_id, is_find=0, is_type=1, page=0):
    inline_kb = InlineKeyboardMarkup(row_width=2)
    if is_find:
        c.execute("select section_id, closes_body_part, closes_type, brand_id "
                  "from finds where find_id = %s", (object_id,))
    else:
        c.execute("select section_id, closes_body_part, closes_type, brand_id from ads where ad_id = %s", (object_id,))
    category_id, closes_body_part, closes_type, brand_id = c.fetchone()
    if is_type:
        closes_type = None
    print(category_id, closes_body_part)
    c.execute("select type_id, type_name from closes_types "
              "where category_id = %s and IF(%s, parent_id = %s, parent_id is NULL) and "
              "body_part = %s and is_type = %s",
              (category_id, closes_type, closes_type, closes_body_part, is_type))
    all_brands = c.fetchall()
    offset = 10
    offset_brands = all_brands[page * offset:(page + 1) * offset]
    for type_id, type_name in offset_brands:
        if is_type:
            one_callback = f'selectClosesType_{object_id}_{type_id}_{is_find}'
        else:
            one_callback = f'selectClosesKind_{object_id}_{type_id}_{is_find}'
        inline_kb.insert(InlineKeyboardButton(text=f'{type_name}',
                                              callback_data=one_callback))
    inline_kb.row(InlineKeyboardButton(text=f'<<' if page > 0 else '',
                                       callback_data=f'selectClothesTypesPage_{object_id}_'
                                                     f'{is_type}_{is_find}_{page - 1}'),
                  InlineKeyboardButton(text=f'>>' if page + 1 < math.ceil(len(all_brands) / offset) else '',
                                       callback_data=f'selectClothesTypesPage_{object_id}_'
                                                     f'{is_type}_{is_find}_{page + 1}'))
    if not brand_id:
        if is_type or 1:
            callback_data = f'setBodyPart_{object_id}_{closes_body_part}_{is_find}'
        else:
            callback_data = f'selectPartClothes_{object_id}_{is_find}_1'
    else:
        callback_data = f'typeBrandClothes_{object_id}_{is_find}'
    inline_kb.row(InlineKeyboardButton(text=f'↩ Назад',
                                       callback_data=callback_data))
    return inline_kb


async def clothes_brands(c, object_id, is_find=0, is_closes_part=0, select_brand=1, page=0):
    inline_kb = InlineKeyboardMarkup(row_width=2)
    if not is_find:
        c.execute("select category_id, section_id, brand_id, closes_body_part "
                  "from ads where ad_id = %s", (object_id,))
    else:
        c.execute("select category_id, section_id, brand_id, closes_body_part "
                  "from finds where find_id = %s", (object_id,))
    category_id, section_id, ad_brand_id, closes_body_part = c.fetchone()
    print(section_id, ad_brand_id, is_closes_part)
    c.execute("select brand_id, brand_name from brands where category_id = %s and "
              "clothes_type = %s",
              (section_id, closes_body_part))
    all_brands = c.fetchall()
    offset = 10
    offset_brands = all_brands[page * offset:(page + 1) * offset]
    for brand_id, brand_name in offset_brands:
        inline_kb.insert(InlineKeyboardButton(text=f'{brand_name}',
                                              callback_data=f'{"selectClothesBrand" if select_brand else "selectClothesPart"}_'
                                                            f'{object_id}_{brand_id}_'
                                                            f'{is_find}'))
    inline_kb.row(InlineKeyboardButton(text=f'<<' if page > 0 else '',
                                       callback_data=f'selectClothesBrandPage_{object_id}_{is_find}_{page - 1}'),
                  InlineKeyboardButton(text=f'>>' if page + 1 < math.ceil(len(all_brands) / offset) else '',
                                       callback_data=f'selectClothesBrandPage_{object_id}_{is_find}_{page + 1}'))
    if is_closes_part:
        callback_data = f'typeBrandClothes_{object_id}_{is_find}'
    elif select_brand:
        callback_data = f'setBodyPart_{object_id}_{closes_body_part}_{is_find}'
    else:
        callback_data = f'createAdSelectCategory_{category_id}_{section_id}'
    inline_kb.row(InlineKeyboardButton(text=f'↩ Назад',
                                       callback_data=callback_data))
    return inline_kb


async def get_brands(c, object_id=None, is_find=0, parent_id=None, page=0, is_edit=0):
    inline_kb = InlineKeyboardMarkup(row_width=2)
    if not is_find:
        c.execute("select category_id, section_id from ads where ad_id = %s", (object_id,))
    else:
        c.execute("select category_id, section_id from finds where find_id = %s", (object_id,))
    category_id, section_id = c.fetchone()
    c.execute("select brand_id, brand_name "
              "from brands "
              "where category_id = %s and IF(%s, parent_id = %s, parent_id is NULL)",
              (section_id, parent_id, parent_id))
    all_brands = c.fetchall()
    offset = 10
    type_text = "Ad" if not is_find else "Find"
    offset_brands = all_brands[page * offset:(page + 1) * offset]
    for brand_id, brand_name in offset_brands:
        if is_edit:
            query = f'editBrandFind_{object_id}_{brand_id}'
        else:
            query = f'selectBrand{type_text}_{object_id}_{brand_id}'
        inline_kb.insert(InlineKeyboardButton(text=f'{brand_name}',
                                              callback_data=query))
    if is_edit:
        page_query = 'editListBrand'
    else:
        page_query = 'listBrands'
    inline_kb.row(InlineKeyboardButton(text=f'<<' if page > 0 else '',
                                       callback_data=f'{page_query}_{object_id}_{parent_id}_{is_find}_{page - 1}'),
                  InlineKeyboardButton(text=f'>>' if page + 1 < math.ceil(len(all_brands) / offset) else '',
                                       callback_data=f'{page_query}_{object_id}_{parent_id}_{is_find}_{page + 1}'))
    if is_find:
        if is_edit:
            back_query = f'backToFind_{object_id}'
        else:
            back_query = f'findAdSelectCategory_{category_id}'
    else:
        if not parent_id:
            back_query = f'createAdSelectCategory_{category_id}'
        else:
            c.execute("select parent_id from brands where brand_id = %s", (parent_id,))
            brand_parent_id = c.fetchone()[0]
            print(brand_parent_id)
            if not brand_parent_id:
                back_query = f'createAdSelectCategory_{category_id}_{section_id}'
            else:
                back_query = f'selectBrand{type_text}_{object_id}_{brand_parent_id}'
    inline_kb.row(InlineKeyboardButton(text=f'↩ Назад',
                                       callback_data=back_query))
    return inline_kb


async def multiple_brands(c, object_id=None, parent_id=None, page=0):
    inline_kb = InlineKeyboardMarkup(row_width=2)
    c.execute("select category_id, section_id from finds where find_id = %s", (object_id,))
    category_id, section_id = c.fetchone()
    c.execute("select brand_id, brand_name "
              "from brands "
              "where category_id = %s and IF(%s, parent_id = %s, parent_id is NULL)",
              (section_id, parent_id, parent_id))
    all_brands = c.fetchall()
    offset = 10
    offset_brands = all_brands[page * offset:(page + 1) * offset]
    c.execute("select brand_id from find_brands where find_id = %s", (object_id,))
    all_find_brands = [x[0] for x in c.fetchall()]
    for brand_id, brand_name in offset_brands:
        query = f'editFindModel_{object_id}_{parent_id}_{brand_id}_{page}'
        inline_kb.insert(InlineKeyboardButton(text=f'{"✅" if brand_id in all_find_brands else "⬜"} {brand_name}',
                                              callback_data=query))
    page_query = 'editFindModel'
    inline_kb.row(InlineKeyboardButton(text=f'<<' if page > 0 else '',
                                       callback_data=f'{page_query}_{object_id}_{parent_id}_0_{page - 1}'),
                  InlineKeyboardButton(text=f'>>' if page + 1 < math.ceil(len(all_brands) / offset) else '',
                                       callback_data=f'{page_query}_{object_id}_{parent_id}_0_{page + 1}'))
    back_query = f'backToFind_{object_id}'
    inline_kb.row(InlineKeyboardButton(text=f'💾 Сохранить',
                                       callback_data=back_query))
    inline_kb.row(InlineKeyboardButton(text=f'↩ Назад',
                                       callback_data=back_query))
    return inline_kb


async def get_find_param_keyboard(c, param_id, find_id, page=0):
    param_id = int(param_id)
    inline_kb = InlineKeyboardMarkup(row_width=2)
    c.execute("select brand_id, model_id, serial_id, section_id from finds where find_id = %s", (find_id,))
    old_brand_id, model_id, serial_id, section_id = c.fetchone()
    # brand_id = model_id if not serial_id else serial_id
    # print(param_id, brand_id)
    c.execute("select brand_id from find_brands where find_id = %s", (find_id,))
    selected_brands = [x[0] for x in c.fetchall()] + [old_brand_id]
    print(find_id, selected_brands)
    param_options = []
    for brand_id in selected_brands:
        c.execute(
            "select option_id, (select option_name from options where options.option_id = brand_params.option_id), "
            "param_position "
            "from brand_params "
            "where param_id = %s and brand_id = %s",
            (param_id, brand_id))
        param_options_brand = c.fetchall()
        print(brand_id, param_id, param_options_brand)
        param_options += param_options_brand
    if section_id == 13:
        param_options = [(340, 'Lightning', 1), (361, '3,5', 1)]
    # if section_id == 28:
    #     c.execute(
    #         "select option_id, (select option_name from options where options.option_id = brand_params.option_id), "
    #         "param_position "
    #         "from brand_params "
    #         "where param_id = %s and brand_id = %s",
    #         (param_id, brand_id))
    #     param_options = c.fetchall()
    print(param_options)
    c.execute("select option_id from find_options where find_id = %s and param_id = %s", (find_id, param_id))
    ad_options = [x[0] for x in c.fetchall()]
    print(ad_options)
    offset = 12
    offset_param_options = param_options[page * offset:(page + 1) * offset]
    showed_options = []
    if offset_param_options[0][0] == 0:
        c.execute("select option_id, option_name, 1 from options where param_id = %s", (param_id,))
        offset_param_options = c.fetchall()
    for one_param in offset_param_options:
        option_id, option_name, param_position = one_param
        if option_id not in showed_options:
            button = InlineKeyboardButton(text=f'{"✅" if option_id in ad_options else "⬜"} {option_name}',
                                          callback_data=f'selectFindParamOption_{find_id}_{param_id}_{option_id}')
            showed_options.append(option_id)
            if offset_param_options.index(one_param):
                inline_kb.insert(button)
            else:
                inline_kb.row(button)
    all_param_options = [x[0] for x in offset_param_options]
    print(set(all_param_options), set(ad_options))
    selected_all = set(all_param_options) == set(ad_options)
    c.execute("select param_type from params where param_id = %s", (param_id,))
    param_type = c.fetchone()[0]
    if param_type in ('multilist', 'list'):
        inline_kb.row(InlineKeyboardButton(text=f'{"✅" if selected_all else "⬜"} Всё сразу',
                                           callback_data=f'selectFindParamOption_{find_id}_'
                                                         f'{param_id}_{0}'))
    back_query = f'backToFind_{find_id}'
    inline_kb.row(InlineKeyboardButton(
        text=f'Пропустить ⏩' if not ad_options else ('' if not ad_options else 'Сохранить 💾'),
        callback_data=f'backToFind_{find_id}'))
    inline_kb.row(InlineKeyboardButton(text=f'↩ Назад',
                                       callback_data=back_query))
    inline_kb.insert(InlineKeyboardButton(text=f'🔄 Сбросить поиск',
                                          callback_data=f'skipSearch'))
    return inline_kb


async def get_notify_menu(c, object_id):
    inline_kb = InlineKeyboardMarkup(row_width=2)
    c.execute("select is_active from finds where is_notify = 1 and find_id = %s", (object_id,))
    is_active = c.fetchone()[0]
    inline_kb.insert(InlineKeyboardButton(text=f'Приостановить ⏸' if is_active else 'Возобновить ▶',
                                          callback_data=f'pauseNotify_{object_id}'))
    inline_kb.insert(InlineKeyboardButton(text=f'Удалить ❌',
                                          callback_data=f'deleteNotify_{object_id}'))
    return inline_kb


async def see_photos(object_id):
    inline_kb = InlineKeyboardMarkup(row_width=2)
    inline_kb.insert(InlineKeyboardButton(text=f'📷 Все фото',
                                          callback_data=f'editAdPhotos_{object_id}'))
    return inline_kb


async def get_ad_menu(c, object_id, user_id, is_edit=0, is_publish=0, page=0, count_pages=0, find_id=0,
                      is_favourites=0):
    inline_kb = InlineKeyboardMarkup(row_width=2)
    if not find_id:
        c.execute("select user_id, is_pause, tariff_price from ads where ad_id = %s", (object_id,))
        ad_user_id, is_pause, tariff_price = c.fetchone()
    else:
        c.execute("select user_id, is_notify from finds where find_id = %s", (find_id,))
        ad_user_id, is_notify = c.fetchone()
    if int(ad_user_id) == int(user_id) and not find_id and not is_favourites:
        if is_edit:
            inline_kb.insert(InlineKeyboardButton(text=f'Название',
                                                  callback_data=f'editAd_name_{object_id}'))
            inline_kb.insert(InlineKeyboardButton(text=f'Описание',
                                                  callback_data=f'editAd_description_{object_id}'))
            inline_kb.insert(InlineKeyboardButton(text=f'Категория',
                                                  callback_data=f'editAd_name_{object_id}'))
            inline_kb.insert(InlineKeyboardButton(text=f'Цена',
                                                  callback_data=f'editAd_price_{object_id}'))
            inline_kb.insert(InlineKeyboardButton(text=f'↩ Назад',
                                                  callback_data=f'seeAd_{object_id}'))
        elif is_publish:
            inline_kb.insert(InlineKeyboardButton(text=f'✅ Опубликовать - {tariff_price}₽',
                                                  callback_data=f'publishAd_{object_id}'))
            inline_kb.row(InlineKeyboardButton(text=f'↩ Назад',
                                               callback_data=f'returnToCreateAd_{object_id}'))
            inline_kb.row(InlineKeyboardButton(text=f'🔄 Сбросить объявление',
                                               callback_data=f'resetAd_{object_id}'))
        else:
            if count_pages > 1:
                prev_page = page - 1
                prev_page = count_pages - 1 if prev_page < 1 else prev_page
                next_page = page + 1
                next_page = 1 if next_page > count_pages else next_page
                inline_kb.row(InlineKeyboardButton(text=f'⏪',
                                                   callback_data=f'showAds_{prev_page}'),
                              InlineKeyboardButton(text=f'{page}/{count_pages}',
                                                   callback_data=f' '),
                              InlineKeyboardButton(text=f'⏩',
                                                   callback_data=f'showAds_{next_page}'))
            # inline_kb.insert(InlineKeyboardButton(text=f'⌛ Продлить',
            #                                       callback_data=f'extendAd_{object_id}'))
            # inline_kb.insert(InlineKeyboardButton(text=f'⏸ Приостановить' if not is_pause else f'▶ Возобновить',
            #                                       callback_data=f'stopAd_{object_id}'))
            inline_kb.insert(InlineKeyboardButton(text=f'📷 Все фото',
                                                  callback_data=f'seeAdPhotos_{object_id}'))
            inline_kb.insert(InlineKeyboardButton(text=f'❌ Удалить',
                                                  callback_data=f'resetAd_{object_id}'))
    elif is_favourites:
        prev_page = page - 1
        prev_page = count_pages - 1 if prev_page < 1 else prev_page
        next_page = page + 1
        next_page = 0 if next_page >= count_pages else next_page
        inline_kb.row(InlineKeyboardButton(text=f'⏪',
                                           callback_data=f'favourites_{prev_page}'),
                      InlineKeyboardButton(text=f'{page + 1}/{count_pages}',
                                           callback_data=f' '),
                      InlineKeyboardButton(text=f'⏩',
                                           callback_data=f'favourites_{next_page}'))
        c.execute("select count(*) from favourites_ads where ad_id = %s and user_id = %s", (object_id, user_id))
        is_favourite = c.fetchone()[0]
        inline_kb.insert(InlineKeyboardButton(text=f'📷 Все фото',
                                              callback_data=f'seeAdPhotos_{object_id}'))
        inline_kb.insert(InlineKeyboardButton(text=f'🗂 В избранное' if not is_favourite else '🗂 В избранном',
                                              callback_data=f'addFavourites_{object_id}_{0}_{page}'))
        inline_kb.row(InlineKeyboardButton(text=f'✖ Закрыть меню',
                                           callback_data=f'skipSearch'))
    elif int(user_id) != int(ad_user_id) or not is_edit:
        if find_id:
            prev_page = page - 1
            prev_page = count_pages - 1 if prev_page < 0 else prev_page
            next_page = page + 1
            next_page = 0 if next_page >= count_pages else next_page
            if count_pages > 1 and not is_notify:
                inline_kb.row(InlineKeyboardButton(text=f'⏪',
                                                   callback_data=f'search_{find_id}_{prev_page}'),
                              InlineKeyboardButton(text=f'{page + 1}/{count_pages}',
                                                   callback_data=f' '),
                              InlineKeyboardButton(text=f'⏩',
                                                   callback_data=f'search_{find_id}_{next_page}'))
            c.execute("select count(*) from favourites_ads where ad_id = %s and user_id = %s", (object_id, user_id))
            is_favourite = c.fetchone()[0]
            inline_kb.insert(InlineKeyboardButton(text=f'📷 Все фото',
                                                  callback_data=f'seeAdPhotos_{object_id}'))
            inline_kb.insert(InlineKeyboardButton(text=f'🗂 В избранное' if not is_favourite else '🗂 В избранном',
                                                  callback_data=f'addFavourites_{object_id}_{find_id}_{page}'))
            if not is_notify:
                inline_kb.insert(InlineKeyboardButton(text=f'⬅ Изм. поиск',
                                                      callback_data=f'backToFind_{find_id}'))
            inline_kb.insert(InlineKeyboardButton(text=f'⚠ Ошибка',
                                                  callback_data=f'adWarning_{object_id}'))
            if not is_notify:
                inline_kb.row(InlineKeyboardButton(text=f'✖ Завершить поиск',
                                                   callback_data=f'skipSearch'))
            else:
                inline_kb.row(InlineKeyboardButton(text=f'✖ Закрыть',
                                                   callback_data=f'hide'))
        else:
            inline_kb.row(InlineKeyboardButton(text=f'✖ Закрыть меню',
                                               callback_data=f'hide'))
    return inline_kb


def balance_menu():
    inline_kb = InlineKeyboardMarkup(row_width=2)
    inline_kb.row(InlineKeyboardButton(text=f'➕ Пополнить баланс',
                                       callback_data=f'depositMoney'))
    return inline_kb
