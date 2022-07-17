import math

import utm

from math import radians, sqrt, sin, atan2, cos

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def distance_haversine(lat1, lon1, lat2, lon2):
    # approximate radius of earth in km
    R = 6363.0 * 1000
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance


def distance_cartesian(x1, y1, x2, y2):
    dx = x1 - x2
    dy = y1 - y2
    return sqrt(dx * dx + dy * dy)


def get_distance_points(lat_1, long_1, lat_2, long_2):
    lat_1, long_1, lat_2, long_2 = float(lat_1), float(long_1), float(lat_2), float(long_2)

    x1, y1, z1, u = utm.from_latlon(lat_1, long_1)
    x2, y2, z2, u = utm.from_latlon(lat_2, long_2)
    haver = distance_haversine(lat_1, long_1, lat_2, long_2)
    carte = distance_cartesian(x1, y1, x2, y2)
    return int((int(haver) + int(carte)) / 2)


async def find_cities(c, latitude, longitude, by_distance=0):
    c.execute("select city_id, city_name, city_latitude, city_longitude from all_cities")
    all_cities = c.fetchall()
    confirm_cities = {}
    for one_city in all_cities:
        city_id, city_name, city_latitude, city_longitude = one_city
        if latitude:
            distance = get_distance_points(latitude, longitude, city_latitude, city_longitude)
        else:
            distance = 100
        if distance/1000 < 100 or latitude == 0:
            # print(one_city, distance)
            # print('ok')
            confirm_cities[city_id] = [city_name, city_latitude, city_longitude, distance]
    confirm_cities = {k: v for k, v in sorted(confirm_cities.items(), key=lambda item: item[1][3 if by_distance else 0])}
    return confirm_cities


async def get_inline_kb(c, user_id, city_id=0, page=0, latitude=0, longitude=0, query='selectCity', by_distance=1):
    page = int(page)
    if city_id:
        c.execute("select city_latitude, city_longitude from all_cities where city_id = %s", (city_id,))
        latitude, longitude = c.fetchone()
    nearest_cities = await find_cities(c, latitude, longitude, by_distance)
    offset = 7 if by_distance else 16
    inline_kb = InlineKeyboardMarkup(row_width=1 if by_distance else 2)
    nearest_cities_list = list()
    for one_city_id in list(nearest_cities.keys()):
        nearest_cities_list.append(one_city_id)
    count_pages = math.ceil(len(nearest_cities_list) / offset)
    count_all_cities = len(nearest_cities_list)
    if count_pages <= page:
        page = count_pages - 1
    if count_all_cities / offset < page or 1:
        cities_offset = list(nearest_cities_list)[offset * page:offset * (page + 1)]
    else:
        cities_offset = list(nearest_cities.keys())[offset * (count_pages - 1):offset * count_pages]
        page = count_pages
    prev_page = page - 1
    next_page = page + 1
    c.execute("select city_id from users where user_id = %s", (user_id,))
    try:
        user_city_id = c.fetchone()[0]
    except:
        user_city_id = None
    for city_id in cities_offset:
        city_name, city_latitude, city_longitude, distance = nearest_cities[city_id]
        inline_kb.insert(InlineKeyboardButton(text=f'{"🔹" if user_city_id == city_id else ""} '
                                                   f'{city_name}',
                                              callback_data=f'{query}_{city_id}_{page}'))
    inline_kb.row(InlineKeyboardButton(text=f'◀' if page > 0 else '',
                                       callback_data=f'showCities_{prev_page}_{user_id}_{query}_{by_distance}'),
                  InlineKeyboardButton(text=f'{page + 1}/{count_pages}' if count_pages > 1 else '',
                                       callback_data=f' '),
                  InlineKeyboardButton(text=f'▶' if page < count_pages - 1 else '',
                                       callback_data=f'showCities_{next_page}_{user_id}_{query}_{by_distance}'))
    if query == 'selectCity' and user_city_id:
        inline_kb.row(InlineKeyboardButton(text=f'⏩ Продолжить',
                                           callback_data=f'confirmSelectedCity_{user_id}'))
    inline_kb.row(InlineKeyboardButton(text=f'↩ Вернуться в начало',
                                       callback_data=f'getSelectCityMethods'))
    return inline_kb
