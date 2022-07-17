import transliterate


async def id_to_name(c, city_id):
    c.execute("select city_name from all_cities where city_id = %s",
              (city_id,))
    try:
        city_name = c.fetchone()[0]
    except:
        city_name = 'удаленный'
    return city_name


async def name_to_id(c, city_name):
    c.execute("select city_id from all_cities where city_name = %s",
              (city_name,))
    try:
        city_id = c.fetchone()[0]
    except:
        city_id = 0
    return city_id


async def timezone_by_id(c, city_id):
    c.execute("select timezone from all_cities where city_id = %s",
              (city_id,))
    timezone = c.fetchone()[0]
    return timezone


async def check_city_by_name(c, city_name, city_type, city_area=0):
    eng_text = transliterate.translit(city_name, 'ru', reversed=True)
    rus_text = transliterate.translit(city_name, 'ru', reversed=False)
    city_type_name = 'область' if city_type == 'area' else ('край' if city_type == 'region' else '')
    print(city_type)
    if city_type in ('area', 'region'):
        c.execute("select city_id, city_area from all_cities "
                  "where (city_area like %s or city_area like %s) and city_area like %s group by city_area "
                  "limit 50",
                  (f'%{eng_text}%', f'%{rus_text}%', f'%{city_type_name}%',))
    else:
        c.execute("select city_id, city_name from all_cities "
                  "where (city_name like %s or city_name like %s) and "
                  "city_area = (select city_area from all_cities where city_id = %s limit 1) "
                  "group by city_name "
                  "limit 50",
                  (f'%{eng_text}%', f'%{rus_text}%', city_area,))
    all_city_names = c.fetchall()
    print(all_city_names)
    return all_city_names
