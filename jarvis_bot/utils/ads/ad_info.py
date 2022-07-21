from keyboards.inline import dynamic_keyboards
from aiogram.types.message import InputMedia, MediaGroup


async def get_ad_text(c, object_id, user_id=0, is_preview=0):
    c.execute("select ad_contacts, ad_description, section_id, ad_price, user_id, is_pause, "
              "date_format(date_close, '%d-%m-%y %h:%i'), brand_id, serial_id, model_id, city_id "
              "from ads where ad_id = %s", (object_id,))
    ad_contacts, ad_description, category_id, ad_price, ad_user_id, is_pause, date_close, \
    brand_id, serial_id, model_id, city_id = c.fetchone()
    params_options_text = []
    if brand_id:
        c.execute("select brand_name from brands where brand_id = %s", (brand_id,))
        brand_name = c.fetchone()[0]
        params_options_text.append(f'<b>Бренд:</b> {brand_name}')
    if serial_id:
        c.execute("select brand_name from brands where brand_id = %s", (serial_id,))
        serial_name = c.fetchone()[0]
        params_options_text.append(f'<b>Серия:</b> {serial_name}')
    if model_id:
        c.execute("select brand_name from brands where brand_id = %s", (model_id,))
        model_name = c.fetchone()[0]
        params_options_text.append(f'<b>Модель:</b> {model_name}')
    c.execute("select category_name from categories where category_id = %s", (category_id,))
    category_name = c.fetchone()[0]
    c.execute("select city_name from all_cities where city_id = %s", (city_id,))
    try:
        city_name = c.fetchone()[0]
    except:
        city_name = 'не найден'
    c.execute("select param_id from ad_options where ad_id = %s", (object_id,))
    all_param_ids = list(set([x[0] for x in c.fetchall()]))
    for param_id in all_param_ids:
        c.execute("select option_id from ad_options where param_id = %s and ad_id = %s", (param_id, object_id))
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
        try:
            param_name = c.fetchone()[0]
        except:
            param_name = 'удаленный'
        all_options_names = ", ".join(all_options_names)
        params_options_text.append(f'<b>{param_name}</b>: {all_options_names}')
    params_options_text = "\n".join(params_options_text)
    ad_description = 'без описания' if not ad_description else ad_description
    ad_photos = await get_ad_photos(c, object_id)
    photo_ad = "" if (len(ad_photos[0]) > 1 or not len(ad_photos[0])) else f'<a href="{ad_photos[0][0]}">&#8203;</a>'
    ad_price = '{0:,}'.format(ad_price).replace(',', ' ')
    return_text = f'{photo_ad}' \
                  f'{params_options_text}\n\n' \
                  f'📝 <b>Описание:</b> {ad_description}\n\n' \
                  f'🏠 <b>Город:</b> {city_name}\n' \
                  f'💰 <b>Цена:</b> {ad_price} рублей\n\n' \
                  f'📱 <b>Контакты:</b> {ad_contacts}\n\n' \
                  f'Объявление создано в категории <b>{category_name}</b>'
    return return_text


async def params_text(c, object_id, is_find):
    if is_find:
        c.execute("select * from finds where find_id = %s", (object_id,))
    else:
        c.execute("select * from ads where ad_id = %s", (object_id,))


async def get_ad_photos(c, ad_id):
    c.execute("select photo_link from ads_photos where ad_id = %s limit 10", (ad_id,))
    all_photos_links = [x[0] for x in c.fetchall()]
    if not all_photos_links:
        c.execute("select IF(model_id, model_id, serial_id) from ads where ad_id = %s", (ad_id,))
        brand_id = c.fetchone()[0]

        c.execute("select option_id from ad_options where ad_id = %s", (ad_id,))
        for option_id in [x[0] for x in c.fetchall()]:

            c.execute("select brand_param_id "
                      "from brand_params where brand_id = %s and option_id = %s", (brand_id, option_id))
            for brand_param_id in [x[0] for x in c.fetchall()]:

                c.execute("select photo_link from brands_photos where brand_id = %s and color_id = %s",
                          (brand_id, brand_param_id))
                all_photos_links = [x[0] for x in c.fetchall()]
                if all_photos_links:
                    break
    all_photos_links_group = MediaGroup(medias=[InputMedia(media=i) for i in all_photos_links])
    return all_photos_links, all_photos_links_group


async def show_ads(c, page=1, user_id=0, is_my_ads=1):
    c.execute("select ad_id from ads where user_id = %s and is_pause = 0 and is_paid = 1 order by ad_id desc",
              (user_id,))
    users_ads = [x[0] for x in c.fetchall()]
    inline_kb = None
    if not users_ads:
        result_text = "Список Ваших объявлений пуст..."
    else:
        ad_id = users_ads[page - 1]
        result_text = await get_ad_text(c, ad_id)
        inline_kb = await dynamic_keyboards.get_ad_menu(c, ad_id, user_id, page=page,
                                                        count_pages=len(users_ads))
    return result_text, inline_kb
