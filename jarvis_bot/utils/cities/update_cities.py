import csv


async def update_cities(c, conn):
    with open('./data/data.csv', newline='', encoding='utf-8') as File:
        reader = csv.reader(File)
        c.execute("delete from all_cities where city_population < 10000")
        conn.commit()
        for row in reader:
            if row[4] == "г" or 1:
                city_area = row[1]
                city_name = row[3]
                city_population = row[5]
                city_latitude = row[9]
                city_longitude = row[10]
                print(city_area, city_name, city_population, city_latitude, city_longitude)
                c.execute("select count(*) from all_cities "
                          "where city_name = %s and city_area = %s",
                          (city_name, city_area))
                if not c.fetchone()[0]:
                    try:
                        if int(city_population) > 10000:
                            c.execute("insert into all_cities "
                                      "(city_name, city_area, city_population, city_latitude, city_longitude) "
                                      "values (%s, %s, %s, %s, %s)",
                                      (city_name, city_area, city_population, city_latitude, city_longitude))
                    except Exception as e:
                        print(e)
                    conn.commit()
