from keyboards.inline import dynamic_keyboards
from utils.ads import ad_params


async def send_step_message(c, conn, message, ad_id, param_id, option_id=0, page_id=0):
    c.execute("select param_type from params where param_id = %s", (param_id,))
    param_type = c.fetchone()[0]
    c.execute("select last_brand_id from ads where ad_id = %s", (ad_id,))
    last_brand_id = c.fetchone()[0]
    # c.execute("select option_id from brand_params where param_id = %s and brand_id = %s",
    #           (param_id, last_brand_id))
    # all_param_options = [x[0] for x in c.fetchall()]
    c.execute("select option_id from ad_options where param_id = %s and ad_id = %s", (param_id, ad_id))
    all_ad_param_options = [x[0] for x in c.fetchall()]
    if param_type == 'list':
        if option_id:
            c.execute("delete from ad_options where param_id = %s and ad_id = %s", (param_id, ad_id))
            if option_id not in all_ad_param_options:
                c.execute("insert into ad_options (ad_id, option_id, param_id) "
                          "values (%s, %s, %s)", (ad_id, option_id, param_id))
            conn.commit()
        await ad_params.get_step(c, message, ad_id, param_id, page_id=page_id)
    else:
        if option_id:

            if option_id in all_ad_param_options:
                c.execute("delete from ad_options where option_id = %s and ad_id = %s", (option_id, ad_id))
            else:
                c.execute("insert into ad_options (ad_id, option_id, param_id) "
                          "values (%s, %s, %s)", (ad_id, option_id, param_id))
            conn.commit()
        else:
            c.execute("select option_id from options where param_id = %s", (param_id,))
            all_param_options = [x[0] for x in c.fetchall()]
            for k in all_param_options:

                c.execute("select count(*) from ad_options where ad_id = %s and option_id = %s",
                          (ad_id, k))
                if not c.fetchone()[0]:
                    if set(all_param_options) != set(all_ad_param_options):
                        c.execute("insert into ad_options (ad_id, option_id, param_id) "
                                  "values (%s, %s, %s)", (ad_id, k, param_id))
                else:

                    if set(all_param_options) == set(all_ad_param_options):
                        c.execute("delete from ad_options where option_id = %s and ad_id = %s",
                                  (k, ad_id))
            conn.commit()
        await message.edit_reply_markup(await dynamic_keyboards.get_ad_param_keyboard(c, ad_id, param_id, page_id))
