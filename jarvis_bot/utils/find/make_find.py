import datetime
import logging

from keyboards.inline import dynamic_keyboards
from loader import bot
from utils.ads import ad_info


async def find_results(c, find_id, start_datetime=(datetime.datetime.now() - datetime.timedelta(days=30))):
    c.execute("select price_limit_id, section_id, city_id, brand_id from finds where find_id = %s", (find_id,))
    price_limit_id, section_id, city_id, main_find_brand_id = c.fetchone()
    c.execute("select start_price, finish_price from category_price_limits where price_limit_id = %s",
              (price_limit_id,))
    try:
        start_price, finish_price = c.fetchone()
    except:
        start_price, finish_price = 0, 0
    if not finish_price:
        finish_price = 99999999999
    c.execute("select option_id, param_id, "
              "(select param_name from params where find_options.param_id = params.param_id) "
              "from find_options where find_id = %s", (find_id,))
    all_options = c.fetchall()
    options_dict = {}
    for op_id, par_id, par_name in all_options:
        if par_id in options_dict.keys():
            old = options_dict[par_id]
            old.append(op_id)
            options_dict[par_id] = old
        else:
            options_dict[par_id] = [op_id]
    c.execute("select brand_id from find_brands where find_id = %s", (find_id,))
    find_brands = c.fetchall()
    find_brands = [x[0] for x in find_brands]
    find_brands.append(main_find_brand_id)

    c.execute("select ad_id, brand_id, serial_id, model_id, main_brand_id from ads "
              "where section_id = %s and ad_price <= %s and "
              "ad_price >= %s and is_paid = 1 and date_create > %s and city_id = %s "
              "and date_close > NOW()",
              (section_id, finish_price, start_price, start_datetime, city_id))
    all_ads = c.fetchall()

    filtered_ads = []
    for ad_id, brand_id, serial_id, model_id, main_brand_id in all_ads:
        c.execute("select param_id, option_id from ad_options where ad_id = %s", (ad_id,))
        all_ad_options = c.fetchall()
        if serial_id in find_brands or model_id in find_brands or brand_id in find_brands or \
                (not serial_id and not model_id and main_brand_id == main_find_brand_id):
            filtered_ads.append(ad_id)
            for ad_param_id, ad_option_id in all_ad_options:
                if ad_param_id in options_dict.keys():
                    if ad_option_id in options_dict[ad_param_id]:
                        pass
                    else:
                        filtered_ads.remove(ad_id)
                        break
    return filtered_ads


async def check_notifications(c, conn):
    c.execute("select find_id, create_date, user_id from finds where close_notifications > NOW()")
    all_finds = c.fetchall()
    for find_id, create_date, user_id in all_finds:
        all_ads = await find_results(c, find_id, start_datetime=create_date)
        for ad_id in all_ads:
            c.execute("select count(*) from notifications_ads where find_id = %s and ad_id = %s",
                      (find_id, ad_id))
            if not c.fetchone()[0]:
                c.execute("insert into notifications_ads (find_id, ad_id) values (%s, %s)", (find_id, ad_id))
                conn.commit()
                inline_kb = await dynamic_keyboards.get_ad_menu(c, ad_id, user_id, find_id=find_id,
                                                                count_pages=0)
                ad_text = await ad_info.get_ad_text(c, ad_id, user_id)
                try:
                    await bot.send_message(user_id, text=f'{ad_text}',
                                           reply_markup=inline_kb)
                except Exception as e:
                    logging.info(e)
    c.execute("delete from ads where date_close < NOW()")
    c.execute("delete from finds where close_notifications < NOW() and is_notify = 1")
    conn.commit()
