import asyncio
import logging

from data import config
from loader import bot
from utils.amo.async_methods import check_rejected, check_leads
from utils.amo.methods import amo_methods
from utils.cities.db import timezone_by_order, name_to_id
from utils.default_tg.default import get_user_menu
from utils.dynamic_keyboards.inline_menu import amo_confirm_deal
from utils.loaders.loader import user_by_form
from utils.loaders.loaders_orders import push_all
from utils.statuses.edit import edit_status_actual_order


def mark_underline(input_text, is_mark=0):
    return f'<u>{input_text}</u>' if is_mark else input_text


async def send_amo_deal(c, conn, deal_id, reply_to_message=None, is_edit=0):
    c.execute("select deal_id, order_id, city, address, service, date_add(start_datetime, interval 3 hour), "
              "count_loaders, car_type, minimum, min_auto,  "
              "floor_descent, floor_rise, rigging, add_service, note, phone, budget, responsible_user, is_push, "
              "edit_address, edit_budget, edit_city, edit_minimum, edit_phone, edit_service, edit_start_datetime, "
              "area_price, add_hour, paid_for_km "
              "from amo_deals where deal_id = %s", (deal_id,))
    deal_id, order_id, city, address, service, start_datetime, count_loaders, car_type, minimum, min_auto, \
    floor_descent, floor_rise, rigging, add_service, note, phone, budget, responsible_user, is_push, edit_address, \
    edit_budget, edit_city, edit_minimum, edit_phone, edit_service, edit_start_datetime, \
    area_price, add_hour, paid_for_km = c.fetchone()
    is_edit = '❗ <b>Заявка была изменена</b>\n\n' if is_edit else ''
    message_text = f'{is_edit}' \
                   f'<b>Адрес:</b> {mark_underline(f"{city}, {address}" if city else address, edit_address or edit_city)}\n\n' \
                   f'<b>Услуги:</b> {mark_underline(service if service else "-", edit_service)}\n\n' \
                   f'<b>Дата начала:</b> {mark_underline(start_datetime, edit_start_datetime)}\n\n' \
                   f'<b>Кол-во грузчиков:</b> {mark_underline(count_loaders if count_loaders else "-", 0)}\n' \
                   f'<b>Доп час:</b> {mark_underline(add_hour if add_hour else "-", 0)}\n' \
                   f'<b>Оплата за км:</b> {mark_underline(paid_for_km if paid_for_km else "-", 0)}\n' \
                   f'<b>Авто:</b> {mark_underline(car_type if car_type else "-", 0)}\n' \
                   f'<b>Бюджет:</b> {mark_underline(budget if budget else "-", edit_budget)}\n' \
                   f'<b>Минималка:</b> {mark_underline(minimum if minimum else "-", edit_minimum)}\n' \
                   f'<b>Минималка авто:</b> {mark_underline(min_auto if min_auto else "-", 0)}\n' \
                   f'<b>Этаж спуск:</b> {mark_underline(floor_descent if floor_descent else "-", 0)}\n' \
                   f'<b>Этаж подъем:</b> {mark_underline(floor_rise if floor_rise else "-", 0)}\n' \
                   f'<b>Такелаж:</b> {mark_underline(rigging if rigging else "-", 0)}\n' \
                   f'<b>Пригород/межгород:</b> {mark_underline(area_price if area_price else "-", 0)}\n' \
                   f'<b>Доп услуги:</b> {mark_underline(add_service if add_service else "-", 0)}\n\n' \
                   f'<b>Примечание:</b> {mark_underline(note if note else "-", 0)}\n\n' \
                   f'<b>Ответственный:</b> {mark_underline(responsible_user, 0)}\n' \
                   f'<b>Телефон клиента:</b> {mark_underline(phone, edit_phone)}'
    city_id = await name_to_id(c, city)
    print(city_id)
    if city_id:
        try:
            c.execute("select (select channel_id from dispatchers_list "
                      "where dispatchers_list.dispatcher_id = dispatchers_cities.dispatcher_id) "
                      "from dispatchers_cities where city_id = %s", (city_id,))
            channel_id = c.fetchone()[0]
            message_info = await bot.send_message(channel_id,
                                                  message_text,
                                                  reply_to_message_id=reply_to_message,
                                                  reply_markup=await amo_confirm_deal(deal_id) if not is_edit else None)
            c.execute("update amo_deals set is_push = 1, tg_message_id = %s, edit_address = 0, edit_budget = 0, "
                      "edit_city = 0, edit_minimum = 0, edit_phone = 0, edit_service = 0, edit_start_datetime = 0, "
                      "channel_id = %s "
                      "where deal_id = %s",
                      (message_info.message_id, channel_id, deal_id,))
            conn.commit()
        except Exception as e:
            logging.info(e, exc_info=True)


async def check_push_deals(c, conn):
    leads = amo_methods.get_all_deals()
    await asyncio.sleep(0)
    await check_leads(c, conn, leads)
    rejected_leads = amo_methods.get_rejected_deals()
    await asyncio.sleep(0)
    await check_rejected(c, conn, rejected_leads)
    c.execute("select deal_id from amo_deals where is_push = 0")
    all_deals = c.fetchall()
    for one_deal in all_deals:
        try:
            await send_amo_deal(c, conn, one_deal[0])
        except Exception as e:
            logging.info(e, exc_info=True)
        await asyncio.sleep(0)
    c.execute("select deal_id, is_active, tg_message_id, order_id, channel_id from amo_deals where active_push = 0")
    all_deals = c.fetchall()
    for one_deal in all_deals:
        deal_id, is_active, tg_message_id, order_id, channel_id = one_deal
        c.execute("update amo_deals set active_push = 1 where deal_id = %s", (deal_id,))
        conn.commit()
        try:
            await bot.send_message(channel_id,
                                   'Теперь заявка не актуальна ❌' if is_active == 0 else 'Заявка снова актуальна ✅',
                                   reply_to_message_id=tg_message_id,
                                   reply_markup=await amo_confirm_deal(amo_deal_id=deal_id) if is_active else None)
        except Exception as e:
            logging.info(e, exc_info=True)
        if not is_active:
            status_id = 5
            try:
                order_timezone = await timezone_by_order(c, order_id)
                await edit_status_actual_order(c, conn, order_id, status_id)
                c.execute("update orders set last_push_time = "
                          "date_sub(date_add(UTC_TIMESTAMP(), interval %s hour), interval 20 minute), "
                          "push_number = 3 "
                          "where order_id = %s", (order_timezone, order_id,))
                conn.commit()
                await push_all(c, conn)
                c.execute("select form_id from orders_forms where order_id = %s", (order_id,))
                all_order_forms = [x[0] for x in c.fetchall()]
                c.execute("select address_text from orders where order_id = %s", (order_id,))
                address_text = c.fetchone()[0]
                for one_form in all_order_forms:
                    form_user_id = await user_by_form(c, one_form)
                    try:
                        await bot.send_message(form_user_id,
                                               f'<b>Обрати внимание</b>\n\n'
                                               f'Твой заказ #{order_id} ({address_text}) был отменен!',
                                               reply_markup=get_user_menu(c, form_user_id))
                    except:
                        pass
                c.execute("select id, user_id, message_id from messages_for_delete where order_id = %s", (order_id,))
                all_messages_to_delete = c.fetchall()
                for one_message in all_messages_to_delete:
                    delete_id, one_user_id, one_message_id = one_message
                    try:
                        c.execute("delete from messages_for_delete where id = %s", (delete_id,))
                        conn.commit()
                        await bot.delete_message(chat_id=one_user_id,
                                                 message_id=one_message_id)
                    except Exception as e:
                        await bot.send_message(128885673,
                                               f'{e} 1057')
            except Exception as e:
                logging.info(e)
        await asyncio.sleep(3)
    c.execute("select deal_id, is_active, tg_message_id, channel_id from amo_deals where edit_push = 0")
    all_deals = c.fetchall()
    for one_deal in all_deals:
        deal_id, is_active, tg_message_id, channel_id = one_deal
        c.execute("update amo_deals set edit_push = 1 where deal_id = %s", (deal_id,))
        conn.commit()
        try:
            await send_amo_deal(c, conn, deal_id, tg_message_id, is_edit=1)
        except Exception as e:
            logging.info(e, exc_info=True)
        await asyncio.sleep(3)
