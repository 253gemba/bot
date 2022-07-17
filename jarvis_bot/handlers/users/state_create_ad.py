import logging
import time

from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.default import default_keyboards, default_buttons
from keyboards.inline import dynamic_keyboards
from loader import dp, bot
from states.states import *
from utils.ads import ad_info
from utils.ads.ad_info import get_ad_text
from utils.db_api.python_mysql import mysql_connection
from utils.default_tg import default
from utils.default_tg.default import get_user_menu
from utils.steps import define_step


@dp.message_handler(content_types="any", state=CreateAd.all_states)
async def create_ad_form(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    msg_text = message.text
    conn = mysql_connection()
    c = conn.cursor(buffered=True)
    state_name = await state.get_state()
    state_data = await state.get_data()
    logging.info(f'{user_id} {msg_text}')
    try:
        object_id = state_data['object_id']
    except:
        object_id = 0
    if msg_text == default_buttons.button_reset_ad.text:
        await message.answer("⚠ <b>Вы действительно хотите сбросить заполненный прогресс?</b>",
                             reply_markup=dynamic_keyboards.delete_object(f'resetAd_{object_id}_{0}'))
    elif object_id:
        if state_name == CreateAd.photo.state:
            if msg_text == default_buttons.button_back.text:
                c.execute("select param_id from ad_options where ad_id = %s order by param_id desc", (object_id,))
                try:
                    old_param_id = c.fetchone()[0]
                except:
                    old_param_id = None
                await message.answer("↩ Возвращаю назад",
                                     reply_markup=default_keyboards.ReplyKeyboardRemove())
                await state.finish()
                c.execute("select category_id, section_id from ads where ad_id = %s", (object_id,))
                category_id, section_id = c.fetchone()
                if category_id == 6:
                    await message.answer("<b>Выберите источник фото</b> 👇\n\n"
                                         "💡 <i>\"Наше фото\" - фото, загруженное из интернета</i>",
                                         reply_markup=await dynamic_keyboards.select_type_photo(c, object_id,
                                                                                                old_param_id=old_param_id))
                else:
                    await message.answer("<b>Оцените состояние товара</b>",
                                            reply_markup=await dynamic_keyboards.get_sizes(c, object_id,
                                                                                           param_id=3,
                                                                                           is_find=0))
            elif message.photo or message.document:
                photo_link = await default.get_link_photo(message.photo[-1].file_id)
                c.execute("insert into ads_photos (ad_id, photo_link) values (%s, %s)",
                          (object_id, photo_link,))
                conn.commit()
                photo_id = c.lastrowid
                state_data = await state.get_data()
                messages_to_delete_old = state_data.get('messages_to_delete')
                if messages_to_delete_old:
                    [await bot.delete_message(user_id, i) for i in messages_to_delete_old]
                print(message)
                print(messages_to_delete_old)
                c.execute("select count(*) from ads_photos where media_group_id = %s", (message.media_group_id,))
                if not c.fetchone()[0] or not message.media_group_id:
                    c.execute("update ads_photos set media_group_id = %s "
                              "where photo_id = %s", (message.media_group_id, photo_id,))
                    conn.commit()
                    c.execute("select photo_id, photo_link from ads_photos where ad_id = %s", (object_id,))
                    messages_to_delete = []
                    # for one_photo in c.fetchall():
                    #     send_message = await bot.send_photo(user_id,
                    #                                         photo=one_photo[1],
                    #                                         reply_markup=dynamic_keyboards.delete_photo(
                    #                                             f'deletePhotoAd_{one_photo[0]}'))
                    #     messages_to_delete.append(send_message.message_id)
                    await bot.send_message(user_id,
                                           f'Нажмите, чтобы отредактировать загруженные фото 👇',
                                           reply_markup=await dynamic_keyboards.see_photos(object_id))
                    send_message = await bot.send_message(user_id,
                                                          f'<b>Отправьте еще одно фото или нажмите '
                                                          f'кнопку [{default_buttons.button_continue.text}]</b>',
                                                          reply_markup=default_keyboards.load_photo_menu)
                # messages_to_delete.append(send_message.message_id)
                # await state.update_data(messages_to_delete=messages_to_delete)
            elif msg_text == default_buttons.button_skip.text or msg_text == default_buttons.button_continue.text:
                await CreateAd.next()
                await message.answer(f'<b>Дополните объявление описанием</b>\n\n'
                                     f'💡 Не более 110 символов',
                                     reply_markup=default_keyboards.skip_menu)
            else:
                await message.answer("⚠ <b>Разрешено отправить только фото</b>")
        elif state_name == CreateAd.description.state:
            if msg_text == default_buttons.button_back.text:
                c.execute("select photo_type from ads where ad_id = %s", (object_id,))
                photo_type = c.fetchone()[0]
                if photo_type == 'my':
                    await CreateAd.photo.set()
                    await message.answer("📷 <b>Загрузите до 10 фото</b>",
                                         reply_markup=default_keyboards.ad_price_menu)
                else:
                    try:
                        c.execute("select param_id from ad_options where ad_id = %s order by param_id desc", (object_id,))
                        param_id = c.fetchone()[0]
                    except:
                        param_id = 0
                    # await ad_params.get_step(c, message, object_id, param_id, add_info='photo')
                    message_text = f'<b>Выберите источник фото</b> 👇\n\n' \
                                   f'💡 <i>\"Наше фото\" - фото, загруженное из интернета</i>'
                    if param_id:
                        new_param_id, old_param_id = await define_step.get_last_and_future(c, object_id, param_id)
                    else:
                        old_param_id = 6
                    inline_kb = await dynamic_keyboards.select_type_photo(c, object_id, old_param_id)
                    try:
                        await message.edit_text(text=message_text,
                                                reply_markup=inline_kb)
                    except:
                        await message.answer(text=message_text,
                                             reply_markup=inline_kb)
                    await state.finish()
            elif len(msg_text) < 110:
                await CreateAd.next()
                c.execute("update ads set ad_description = %s where ad_id = %s",
                          (msg_text if msg_text != default_buttons.button_skip.text else None, object_id))
                conn.commit()
                await bot.send_message(user_id,
                                       f'📱 Введите <b>номер телефона</b> в формате +79991234567 или отправьте свой '
                                       f'<b>юзернейм</b>',
                                       reply_markup=default_keyboards.share_phone_username(message.from_user.username))
            else:
                await message.answer("⚠ <b>Разрешено вводить не более 110 символов</b>")
        elif state_name == CreateAd.contact_method.state:
            if '@' not in str(msg_text):
                msg_text = msg_text if not message.contact else message.contact.phone_number
            if msg_text == default_buttons.button_back.text:
                await CreateAd.description.set()
                await message.answer(f'<b>Дополните объявление описанием</b>\n\n'
                                     f'💡 Не более 110 символов',
                                     reply_markup=default_keyboards.skip_menu)
            elif msg_text or ('@' in msg_text[0] and len(msg_text) < 30):
                c.execute("update ads set ad_contacts = %s where ad_id = %s", (msg_text, object_id))
                conn.commit()
                await CreateAd.next()
                await bot.send_message(user_id,
                                       f'💰 Введите <b>стоимость</b> услуги или товара',
                                       reply_markup=default_keyboards.ad_price_menu)
            else:
                await message.answer("⚠ <b>Разрешено отправлять только телефон в формате +79995412323 или "
                                     "юзернейм в формате @username</b>")
        elif state_name == CreateAd.price.state:
            if msg_text == default_buttons.button_back.text:
                await CreateAd.contact_method.set()
                await bot.send_message(user_id,
                                       f'📱 Введите <b>номер телефона</b> в формате +79991234567 или отправьте свой '
                                       f'<b>юзернейм</b>',
                                       reply_markup=default_keyboards.share_phone_username(message.from_user.username))
            else:
                if msg_text.isdigit() and int(msg_text) >= 0:
                    await state.update_data(price=msg_text)
                    c.execute("update ads set ad_price = %s, "
                              "date_close = date_add(NOW(), interval place_days_period day) "
                              "where ad_id = %s", (msg_text, object_id))
                    conn.commit()
                    await state.finish()
                    await message.answer("Проверьте данные объявления 👇",
                                         reply_markup=default_keyboards.ReplyKeyboardRemove())
                    all_photos_links, all_photos_links_group = await ad_info.get_ad_photos(c, object_id)
                    message_text = f"{await ad_info.get_ad_text(c, object_id, is_preview=1)}"
                    inline_kb = await dynamic_keyboards.get_ad_menu(c, object_id, user_id,
                                                                    is_publish=1)
                    if len(all_photos_links) > 1:
                        sent_message = await bot.send_media_group(chat_id=user_id,
                                                                  media=all_photos_links_group)
                        await sent_message[-1].reply(message_text,
                                                     reply_markup=inline_kb)
                    else:
                        await message.answer(message_text,
                                             reply_markup=inline_kb)
                else:
                    await message.answer("⚠ <b>Стоимость можно ввести только в цифрах</b>")
    else:
        if state_name == CreateAd.description.state:
            c.execute("update ads set ad_description = %s where ad_id = %s",
                      (msg_text, object_id))
        if state_name == CreateAd.price.state:
            c.execute("update ads set ad_price = %s where ad_id = %s",
                      (msg_text, object_id))
        conn.commit()
        await bot.send_message(user_id,
                               f'✅ Изменено',
                               reply_markup=get_user_menu(c, user_id))
        result_text = await get_ad_text(c, object_id)
        inline_kb = await dynamic_keyboards.get_ad_menu(c, object_id, user_id, is_edit=1)
        await message.edit_text(result_text,
                                reply_markup=inline_kb,
                                disable_web_page_preview=True)
    conn.commit()
    c.close()
    conn.close()
