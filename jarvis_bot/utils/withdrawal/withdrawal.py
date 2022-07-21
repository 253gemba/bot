from utils.db_api.python_mysql import mysql_connection


def create_withdrawal(user_id, card_num):
    conn = mysql_connection()
    cur = conn.cursor()
    cur.execute('insert into withdrawal (user_id, card_num) values (%s, %s)', (user_id, card_num))
    conn.commit()
    conn.close()


def get_amount(user_id):
    conn = mysql_connection()
    cur = conn.cursor()
    cur.execute('select bonus_balance from referrals where user = %s', (user_id,))
    result = cur.fetchone()[0]
    conn.close()
    return result


def insert_amount(user_id, amount):
    conn = mysql_connection()
    cur = conn.cursor()
    cur.execute('update withdrawal set amount = %s where user_id = %s', (amount, user_id))
    conn.commit()
    cur.execute('update referrals set bonus_balance = bonus_balance - %s where user = %s', (amount, user_id))
    conn.commit()
    conn.close()
