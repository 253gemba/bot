import asyncio
import json
import logging
import uuid

from yookassa import Payment, Configuration

from data import config
from loader import bot
from utils.default_tg.default import get_user_menu, get_bot_username

Configuration.account_id = config.YOOKASSA_SHOP_ID
Configuration.secret_key = config.YOOKASSA_SECRET_KEY


async def create_payment(payment_value='100.00', description="Пополнение баланса", user_id=0):
    print(Configuration.account_id)
    body = {
        "amount": {
            "value": round((float(payment_value) * 1.04), 2),
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": f"https://t.me/{await get_bot_username()}"
        },
        "capture": True,
        "description": f"{description} {user_id} + комиссия 4%",
        "save_payment_method": False
    }
    payment = Payment.create(body, uuid.uuid4())
    result = json.loads(payment.json())
    return result


async def check_payment(payment_id):
    try:
        payment = Payment.find_one(payment_id)
        return json.loads(payment.json())
    except Exception as e:
        logging.info(f'{e}')
        return False


async def update_payments(c, conn, payment_id=0):
    c.execute("select payment_id, user_id, payment_amount, system_id "
              "from payments "
              "where payment_status = 'wait' and "
              "payment_date >= date_sub(now(), interval 12 hour) and (not %s or payment_id = %s)",
              (payment_id, payment_id))
    all_payments = c.fetchall()
    for one_payment in all_payments:
        payment_id, user_id, payment_amount, system_id = one_payment
        payment_info = await check_payment(system_id)
        if payment_info:
            new_status = payment_info['status']
            if new_status == 'succeeded':
                c.execute("update payments set payment_status = 'succeeded' "
                          "where payment_id = %s", (payment_id,))
                conn.commit()
                c.execute("update users set balance = balance + %s "
                          "where user_id = %s", (payment_amount, user_id,))
                conn.commit()
                try:
                    await bot.send_message(user_id,
                                           f'💰 <b>Спасибо, баланс пополнен на {payment_amount}₽!</b>')
                except:
                    pass
