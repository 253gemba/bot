import logging


async def get_last_and_future(c, ad_id, param_id):
    c.execute("select last_brand_id from ads where ad_id = %s", (ad_id,))
    last_brand_id = c.fetchone()[0]
    c.execute("select param_position from brand_params where param_id = %s and brand_id = %s",
              (param_id, last_brand_id))
    try:
        param_position = c.fetchone()[0]
    except:
        param_position = 1
    c.execute("select param_id, param_position "
              "from brand_params where brand_id = %s group by param_id",
              (last_brand_id,))
    brand_params = c.fetchall()
    all_brand_params = dict([(x[1], x[0]) for x in brand_params])
    only_positions = list(set([x[1] for x in brand_params]))
    try:
        now_index = only_positions.index(param_position)
    except:
        now_index = 0
    new_param_id = 'photo' if now_index == len(only_positions) - 1 else only_positions[now_index + 1]
    if str(new_param_id).isdigit():
        new_param_id = all_brand_params[new_param_id]
    old_param_id = 'brand' if now_index == 0 else only_positions[now_index - 1]
    if str(old_param_id).isdigit():
        old_param_id = all_brand_params[old_param_id]
    return new_param_id, old_param_id


async def get_now_last_step(c, object_id, object_type='ad'):
    """
    if returned value less than 0 so it's category!
    [last_step_id, last_param_id], [now_step_id, now_param_id]
    """
    if object_type == 'ad':
        c.execute("select option_id from ad_options where ad_id = %s", (object_id,))
        ad_options = [x[0] for x in c.fetchall()]
        now_step_id = len(ad_options) - 1
        last_step_id = len(ad_options) - 2
        now_param_id, last_param_id = -1, -1
        if ad_options:
            now_param_id = ad_options[-1]
            if len(ad_options) > 1:
                last_param_id = ad_options[-2]
        return [last_step_id, last_param_id], [now_step_id, now_param_id]


async def get_last_step(c, object_id, object_type='ad', now_param_id=0, now_add_info='0'):
    logging.info(f'now_param_id: {now_param_id}; now_add_info: {now_add_info}')
    if object_type == 'ad':
        if now_add_info.isdigit():
            c.execute("select is_tariff_step from category_params where param_id = %s", (now_param_id,))
            try:
                is_tariff_step = c.fetchone()[0]
            except:
                is_tariff_step = 0
            if is_tariff_step:
                return now_param_id, 'tariff'
        c.execute("select param_id from ad_options where ad_id = %s order by param_id", (object_id,))
        ad_params = [x[0] for x in c.fetchall()]
        try:
            index = ad_params.index(int(now_param_id)) - 1
            last_param_id = ad_params[index]
            if index < 0:
                last_param_id = 0
        except Exception as e:
            logging.info(e)
            if ad_params:
                last_param_id = ad_params[-1]
            else:
                last_param_id = 0
        return last_param_id, '0'


async def get_option_by_step_id(c, object_id, object_type='ad', step_id=1):
    if object_type == 'ad':
        c.execute("select option_id from ad_options where ad_id = %s", (object_id,))
        ad_options = [x[0] for x in c.fetchall()]
        now_option_id = ad_options[step_id]
        return now_option_id


async def get_step_by_option_id(c, object_id, object_type='ad', now_option_id=1):
    now_option_id = int(now_option_id)
    if object_type == 'ad':
        c.execute("select option_id from ad_options where ad_id = %s", (object_id,))
        ad_options = [x[0] for x in c.fetchall()]
        step_id = ad_options.index(now_option_id)
        return step_id


async def get_step_by_param_id(c, object_id, object_type='ad', now_param_id=1):
    now_param_id = int(now_param_id)
    if object_type == 'ad':
        c.execute("select param_id from ad_options where ad_id = %s", (object_id,))
        ad_options = [x[0] for x in c.fetchall()]
        step_id = ad_options.index(now_param_id)
        return step_id
    
    
async def get_future_step_by_param(c, object_id, now_param_id, now_add_info='0'):
    """
    функция принимает на вход текущий параметр и доп информацию к нему, а возвращает следующий. Если его нет,
    возвращает 0
    """
    c.execute("select option_id from ad_options where ad_id = %s and param_id = %s", (object_id, now_param_id))
    try:
        now_option_id = c.fetchone()[0]
    except:
        now_option_id = 0
    if not now_add_info.isdigit():
        return now_param_id, '0'
    else:
        c.execute("select section_id from ads where ad_id = %s", (object_id,))
        section_id = c.fetchone()[0]
        # c.execute("select param_id from param_options where option_id = %s", (now_option_id,))
        # param_id = c.fetchone()[0]
        param_id = now_param_id

        c.execute("select param_id, is_tariff_step from category_params "
                  "where category_id = %s and param_id > %s and "
                  "(select count(*) from param_options "
                  "where (parent_id = %s or parent_id is NULL) and "
                  "param_options.param_id = category_params.param_id) limit 1",
                  (section_id, param_id, now_option_id))
        try:
            next_param_id, is_tariff_step = c.fetchone()
        except:
            next_param_id, is_tariff_step = 0, 0
        # next_param_id = 0 if not next_param_id else next_param_id[0]
        next_add_info = 'tariff' if is_tariff_step else '0'

        return next_param_id, next_add_info


async def get_future_step(c, object_id, object_type='ad', now_step_id=None, now_option_id=None, now_param_id=None,
                          now_add_info='0'):
    if object_type == 'ad':
        if now_step_id is None and now_option_id is None:
            step_info = await get_now_last_step(c, object_id, object_type)
            now_step_id, now_option_id = step_info[1][0], step_info[1][1]
        elif now_step_id is not None:
            now_option_id = await get_option_by_step_id(c, object_id, object_type, step_id=now_step_id)
        elif now_option_id is not None:
            now_step_id = await get_step_by_option_id(c, object_id, object_type, now_option_id=now_option_id)
        if now_param_id is not None:
            now_step_id = await get_step_by_param_id(c, object_id, object_type, now_param_id=now_param_id)
        if not now_add_info.isdigit():
            return now_param_id, '0'
        else:

            c.execute("select section_id from ads where ad_id = %s", (object_id,))
            section_id = c.fetchone()[0]
            # c.execute("select param_id from param_options where option_id = %s", (now_option_id,))
            # param_id = c.fetchone()[0]
            param_id = now_param_id

            c.execute("select param_id, is_tariff_step from category_params "
                      "where category_id = %s and param_id > %s and "
                      "(select count(*) from param_options "
                      "where (parent_id = %s or parent_id is NULL) and "
                      "param_options.param_id = category_params.param_id) limit 1",
                      (section_id, param_id, now_option_id))
            try:
                next_param_id, is_tariff_step = c.fetchone()
            except:
                next_param_id, is_tariff_step = 0, 0
            # next_param_id = 0 if not next_param_id else next_param_id[0]

            next_add_info = 'tariff' if is_tariff_step else '0'
            return next_param_id, next_add_info
