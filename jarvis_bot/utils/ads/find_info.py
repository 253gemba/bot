async def get_find_text(c, object_id, count_ads=0):
    c.execute("select section_id, price_limit_id, user_id, brand_id, serial_id, is_notify, closes_body_part, "
              "closes_type, closes_kind, closes_size_type, category_id "
              "from finds where find_id = %s", (object_id,))
    section_id, price_limit_id, user_id, brand_id, serial_id, is_notify, closes_body_part, closes_type, \
    closes_kind, closes_size_type, category_id = c.fetchone()
    c.execute("select brand_id from find_brands where find_id = %s", (object_id,))
    all_find_brands = [x[0] for x in c.fetchall()]
    all_find_brands_names = []
    for k in all_find_brands:
        c.execute("select brand_name from brands where brand_id = %s", (k,))
        all_find_brands_names.append(c.fetchone()[0])
    all_find_brands_names = f'<b>{"Модель" if section_id not in (19,) else "Корпус"}:</b> {", ".join(all_find_brands_names)}' if all_find_brands_names else ''
    # c.execute("select category_name from categories where category_id = %s", (section_id,))
    # category_name = c.fetchone()[0]
    c.execute("select brand_name from brands where brand_id = %s", (brand_id,))
    try:
        brand_name = c.fetchone()[0]
    except:
        brand_name = 'Бренд не найден'
    param_brand_name = "Марка"
    if section_id in (13, 17, 28):
        param_brand_name = "Тип"
    params_options_text = [f'<b>{param_brand_name}:</b> {brand_name}']
    c.execute("select brand_name from brands where brand_id = %s", (serial_id,))
    try:
        brand_name = c.fetchone()[0]
        param_serial_name = "Серия"
        if section_id in (13,):
            param_serial_name = "Марка"
        if section_id in (17,):
            param_serial_name = "Вид"
        params_options_text.append(f'<b>{param_serial_name}:</b> {brand_name}')
    except:
        pass
    if all_find_brands_names:
        params_options_text.append(all_find_brands_names)
    if closes_body_part:
        params_options_text.append(f'<b>Тип одежды:</b> '
                                   f'{"верхняя часть" if closes_body_part == "up" else ("нижняя часть" if closes_body_part == "down" else "обувь")}')
    c.execute("select type_name from closes_types where type_id = %s", (closes_type,))
    try:
        brand_name = c.fetchone()[0]
        params_options_text.append(f'<b>Предмет одежды:</b> {brand_name}')
    except:
        pass
    c.execute("select type_name from closes_types where type_id = %s", (closes_kind,))
    try:
        brand_name = c.fetchone()[0]
        params_options_text.append(f'<b>Вид:</b> {brand_name}')
    except:
        pass
    c.execute("select param_id from find_options where find_id = %s", (object_id,))
    all_param_ids = list(set([x[0] for x in c.fetchall()]))
    for param_id in all_param_ids:
        c.execute("select option_id from find_options where param_id = %s and find_id = %s", (param_id, object_id))
        all_options = [x[0] for x in c.fetchall()]
        all_options_names = []
        for one_option in all_options:
            c.execute("select option_name from options where option_id = %s", (one_option,))
            try:
                option_name = c.fetchone()[0]
            except:
                option_name = "DELETED"
            all_options_names.append(option_name)
        c.execute("select param_name from params where param_id = %s", (param_id,))
        param_name = c.fetchone()[0]
        all_options_names = ", ".join(all_options_names)
        params_options_text.append(f'<b>{param_name}</b>: {all_options_names}')
    print(params_options_text)
    params_options_text = "\n".join(params_options_text)
    # params_options_text = f'<b>ℹ Характеристики:</b>\n{params_options_text}' if params_options_text else ""
    c.execute("select city_id from users where user_id = %s", (user_id,))
    city_id = c.fetchone()[0]
    c.execute("select city_name from all_cities where city_id = %s", (city_id,))
    try:
        city_name = c.fetchone()[0]
    except:
        city_name = 'не установлен'
    if price_limit_id:
        c.execute("select price_limit_id, start_price, finish_price from category_price_limits "
                  "where price_limit_id = %s",
                  (price_limit_id,))
        price_limit_id, start_price, finish_price = c.fetchone()
        if not start_price:
            limit_text = f'До {finish_price}'
        elif not finish_price:
            limit_text = f'Более {start_price}'
        else:
            limit_text = f'От {start_price} до {finish_price}'
    else:
        limit_text = 'не задан'
    warning_text = f'<b>⚠ ВАЖНО: за последнюю неделю я не видел ни одного объявления с выбранными параметрами. ' \
                   f'Чтобы запустить поиск, прошу тебя расширить фильтры: например, увеличить диапазон цены или ' \
                   f'область поиска</b>'
    price_limit_text = f'💰 <b>Диапазон цен:</b> {limit_text}\n\n' if category_id == 6 else ''
    return_text = f'<b>Текущие параметры {"поиска" if not is_notify else "оповещения"} 👇</b>\n\n' \
                  f'{params_options_text}\n\n' \
                  f'{price_limit_text}' \
                  f'🏙 <b>Город:</b> {city_name}\n\n' \
                  f'Ожидаемое количество объявлений в день: {count_ads}\n\n' \
                  f'{warning_text if not count_ads else ""}'
    return return_text
