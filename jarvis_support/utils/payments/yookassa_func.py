import asyncio
import json
import logging
import uuid

from aiogram.types import InlineKeyboardButton
from yookassa import Configuration, Payment

from data import config
from keyboards.inline import dynamic
from loader import bot
from utils.telegram_functions.telegram_work import get_user_menu

# Configuration.account_id = '821095'
# Configuration.secret_key = 'test_LOfEi4QD1UqJkrNxJI3RleyoXkp_Rb8lb4JH28uQR4M'


async def create_payment(payment_value='100.00', description="Оплата обслуживания бота",
                         is_bot_account=1, payment_method_id=None):
    if is_bot_account:
        Configuration.account_id = config.BOT_ACCOUNT_ID
        Configuration.secret_key = config.BOT_SECRET_KEY
    else:
        Configuration.account_id = config.SKYBOTS_ACCOUNT_ID
        Configuration.secret_key = config.SKYBOTS_SECRET_KEY
    body = {
        "amount": {
            "value": payment_value,
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/skybotsru_bot"
        },
        "capture": True,
        "description": description
    }
    if is_bot_account == 1:
        body["save_payment_method"] = True
    if payment_method_id:
        body['payment_method_id'] = payment_method_id
    else:
        body['payment_method_data'] = {
            "type": "bank_card"
        }
    payment = Payment.create(body, uuid.uuid4())
    return json.loads(payment.json())


async def check_payment(payment_id, payment_system):
    try:
        if payment_system == 2:
            Configuration.account_id = config.BOT_ACCOUNT_ID
            Configuration.secret_key = config.BOT_SECRET_KEY
        else:
            Configuration.account_id = config.SKYBOTS_ACCOUNT_ID
            Configuration.secret_key = config.SKYBOTS_SECRET_KEY
        payment = Payment.find_one(payment_id)
        return payment
    except Exception as e:
        logging.info(f'{e}')
        return False


async def check_auto_payments(c, conn):
    c.execute("select bot_id, server_payment, service_payment, server_push, service_push, bot_username, "
              "date_sub(server_date, interval 24 hour) < NOW(), "
              "date_sub(service_date, interval 24 hour) < NOW(), server_date < NOW(), service_date < NOW() "
              "from client_bots "
              "where date_sub(server_date, interval 24 hour) < NOW() and server_push in (0, 1) or "
              "date_sub(service_date, interval 24 hour) < NOW() and service_push in (0, 1)")
    payments_list = c.fetchall()
    for one_payment in payments_list:
        print(f'auto: {one_payment}')
        bot_id, server_payment, service_payment, server_push, service_push, bot_username, \
        is_server_date_yesterday, is_service_date_yesterday, is_server_date_today, is_service_date_today = one_payment
        if (is_service_date_yesterday or is_service_date_today) and service_payment and service_push in (0, 1) or \
                (is_server_date_yesterday or is_server_date_today) and server_payment and server_push in (0, 1):
            c.execute("select user_id from client_users where bot_id = %s", (bot_id,))
            bot_users = c.fetchall()
            if is_server_date_yesterday or is_server_date_today:  # если истекла сегодняшняя или вчерашняя дата оплаты сервера
                c.execute("update client_bots set server_push = %s where bot_id = %s",
                          (2 if is_server_date_today else 1, bot_id,))
            if is_service_date_yesterday or is_service_date_today:
                c.execute("update client_bots set service_push = %s where bot_id = %s",
                          (2 if is_service_date_today else 1, bot_id,))
            conn.commit()
            for one_user in bot_users:
                bot_user_id = one_user[0]
                # bot_user_id = 940108284
                c.execute("select auto_payments from users where user_id = %s", (bot_user_id,))
                auto_payments = c.fetchone()[0]
                service_name = "Сервер" if (is_server_date_yesterday or is_server_date_today) and not server_push else "Обслуживание"
                payment_type = "server" if (is_server_date_yesterday or is_server_date_today) and not server_push else "service"
                if is_server_date_today or is_service_date_today:
                    need_sum = service_payment if is_service_date_today else service_payment
                    success = 0
                    if auto_payments:
                        c.execute("select method_id from users_payment_methods where user_id = %s", (bot_user_id,))
                        payment_methods = c.fetchall()
                        for method_id in payment_methods:
                            method_id = method_id[0]
                            payment_result = await create_payment(need_sum, payment_method_id=method_id)
                            payment_status = payment_result['status']
                            c.execute("insert into payments (user_id, system_id, bot_id, payment_type, "
                                      "months, is_autopayment, payment_status, payment_system) "
                                      "values (%s, %s, %s, %s, 1, 1, %s, 2)",
                                      (bot_user_id, payment_result['id'], bot_id, payment_type,
                                       payment_status if payment_status == 'succeeded' else 'wait'))
                            conn.commit()
                            print(payment_result)
                            if payment_result['status'] == 'succeeded':
                                success = 1
                            else:
                                c.execute("delete from users_payment_methods where method_id = %s",
                                          (method_id,))
                                conn.commit()
                            if success:
                                if payment_type == 'server':
                                    c.execute(
                                        "update client_bots "
                                        "set server_date = date_add(server_date, interval %s month), server_push = 0 "
                                        "where bot_id = %s", (1, bot_id,))
                                elif payment_type == 'service':
                                    c.execute(
                                        "update client_bots "
                                        "set service_date = date_add(service_date, interval %s month), service_push = 0 "
                                        "where bot_id = %s", (1, bot_id,))
                                conn.commit()
                                try:
                                    await bot.send_message(bot_user_id,
                                                           f'✅ <b>Оплата в размере {need_sum} РУБ через автоплатеж '
                                                           f'прошла успешно. Спасибо!</b>\n\n'
                                                           f'Данное уведомление отправлено по боту @{bot_username}\n\n'
                                                           f'<b>С уважением, Ваш помощник SkyBots Контроль</b>',
                                                           reply_markup=get_user_menu(c, bot_user_id))
                                except:
                                    pass
                                break
                        if success:
                            break
                    if not auto_payments or not success:
                        payment_result = await create_payment(need_sum)
                        c.execute("insert into payments (user_id, system_id, bot_id, payment_type, "
                                  "months, is_autopayment, payment_system) "
                                  "values (%s, %s, %s, %s, 1, 0, 2)",
                                  (bot_user_id, payment_result['id'], bot_id, payment_type))
                        conn.commit()
                        try:
                            not_success_text = 'К сожалению, оплата по карте через автоплатеж не прошла' if not success else ''
                            inline_kb = await dynamic.auto_payments(c, bot_user_id, is_bot=bot_id)
                            inline_kb.row(InlineKeyboardButton(text=f'Оплатить (ссылка действует 4ч ⏳)',
                                                               url=f'{payment_result["confirmation"]["confirmation_url"]}'))
                            await bot.send_message(bot_user_id,
                                                   f'👋 <b>Приветствую!</b> {not_success_text}\n\n'
                                                   f'Напоминаю о необходимости оплаты услуг. Сегодня срок действия '
                                                   f'заканчивается. Просьба оплатить услуги в ближайшее время\n\n'
                                                   f'Данное уведомление отправлено по боту @{bot_username}\n\n'
                                                   f'<b>С уважением, Ваш помощник SkyBots Контроль</b>',
                                                   reply_markup=inline_kb)
                        except Exception as e:
                            print(e)
                elif service_push == 0 or server_push == 0:
                    if auto_payments:
                        need_text = f"будет выполнен автоплатеж за услугу <b>{service_name}</b>"
                    else:
                        need_text = f'закончится срок действия услуги <b>{service_name}</b>. Просьба продлить услугу'
                    try:
                        await bot.send_message(bot_user_id,
                                               f'👋 <b>Приветствую!</b>\n\n'
                                               f'Напоминаю, что ровно через сутки '
                                               f'{need_text}\n\n'
                                               f'Данное уведомление отправлено по боту @{bot_username}\n\n'
                                               f'<b>С уважением, Ваш помощник SkyBots Контроль</b>',
                                               reply_markup=await dynamic.auto_payments(c, bot_user_id, is_bot=bot_id))
                    except Exception as e:
                        print(e)
        await asyncio.sleep(0)


async def update_payments(c, conn):
    c.execute("select payment_id, system_id, months, payment_type, bot_id, user_id, payment_system from payments "
              "where payment_status = 'wait' and date_add(payment_datetime, interval 12 hour) > NOW()")
    all_payments = c.fetchall()
    for one_payment in all_payments:
        payment_id, system_id, months, payment_type, bot_id, payment_user_id, payment_system = one_payment
        print(f'payment_sys: {payment_system}')
        payment_info = await check_payment(system_id, payment_system)
        if payment_info:
            print(payment_info)
            new_status = payment_info.status
            saved = 0
            if new_status == 'succeeded':
                try:
                    payment_method_info = payment_info.payment_method
                    print(payment_method_info)
                    method_type = payment_method_info.type
                    method_id = payment_method_info.id
                    db_method_id = 0
                    c.execute("select count(*) from users_payment_methods where method_id = %s", (method_id,))
                    if not c.fetchone()[0]:
                        c.execute("insert into users_payment_methods (method_id, method_type, user_id) "
                                  "values (%s, %s, %s)", (method_id, method_type, payment_user_id))
                        conn.commit()
                        db_method_id = c.lastrowid
                    if db_method_id:
                        saved = payment_method_info.saved
                        if saved:
                            try:
                                card_info = payment_method_info.card
                                print(card_info)
                                try:
                                    card_first6 = card_info.first6
                                except:
                                    card_first6 = "******"
                                card_last4 = card_info.last4
                                card_expiry_year = card_info.expiry_year
                                card_expiry_month = card_info.expiry_month
                                card_card_type = card_info.card_type
                                card_issuer_name = card_info.issuer_name
                                c.execute("update users_payment_methods "
                                          "set card_type = %s, first6 = %s, last4 = %s, expiry_year = %s, "
                                          "expiry_month = %s, issuer_name = %s",
                                          (card_card_type, card_first6, card_last4, card_expiry_year,
                                           card_expiry_month, card_issuer_name))
                                conn.commit()
                            except Exception as e:
                                logging.info(e)
                except Exception as e:
                    logging.info(e)
                c.execute("update payments set payment_status = 'succeeded' "
                          "where payment_id = %s", (payment_id,))
                conn.commit()
                if payment_type == 'server':
                    c.execute("update client_bots "
                              "set server_date = date_add(server_date, interval %s month), server_push = 0 "
                              "where bot_id = %s", (months, bot_id,))
                elif payment_type == 'service':
                    c.execute("update client_bots "
                              "set service_date = date_add(service_date, interval %s month), service_push = 0 "
                              "where bot_id = %s", (months, bot_id,))
                conn.commit()
                c.execute("select date_format(server_date, '%d.%m.%Y %H:%i'), "
                          "date_format(service_date, '%d.%m.%Y %H:%i') "
                          "from client_bots where bot_id = %s", (bot_id,))
                server_date, service_date = c.fetchone()
                date_value = server_date if 'server' in payment_type else service_date
                payment_type_ru = 'сервер' if 'server' in payment_type else 'обслуживание'
                try:
                    await bot.send_message(payment_user_id,
                                           f'<b>Спасибо, платеж получен</b> ✅\n\n'
                                           f'Услуга «{payment_type_ru}» была продлена до {date_value}',
                                           reply_markup=get_user_menu(c, payment_user_id))
                    c.execute("select auto_payments from users where user_id = %s", (payment_user_id,))
                    is_auto_payments = c.fetchone()[0]
                    if not is_auto_payments and saved:
                        await bot.send_message(payment_user_id,
                                               f'<b>🤖 Вы можете включить автоплатежи</b>\n\n'
                                               f'За день до платежа бот предупредит о списании. Автоплатежи '
                                               f'можно будет отменить в личном кабинете',
                                               reply_markup=await dynamic.auto_payments(c, payment_user_id))
                except Exception as e:
                    logging.info(f'{e}', exc_info=True)
        await asyncio.sleep(0)
