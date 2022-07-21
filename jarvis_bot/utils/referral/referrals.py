from hashlib import md5
from utils.db_api.python_mysql import mysql_connection


def create_referral(user_id, c, conn):
    c.execute('select user_id, tg_username from users where user_id = %s', (user_id,))
    unhashed = c.fetchone()[1]
    hashed = md5(unhashed.encode())
    link = hashed.hexdigest()[:20]
    c.execute(
        'insert into referrals (user, referral, bonus_balance, referred) values (%s, %s, %s, %s)',
        (user_id, link, 0, 0))
    conn.commit()


def get_referral(current_user):
    conn = mysql_connection()
    c = conn.cursor()
    c.execute('select attached_referrals from referrals where user = %s', (current_user,))
    link = c.fetchone()
    conn.close()
    return link


def fetch_user_referral(link):
    connect = mysql_connection()
    cursor = connect.cursor(buffered=True)
    cursor.execute('select user from referrals where referral = %s', (link,))
    user_id = cursor.fetchone()
    connect.close()
    return user_id


def attach_referral(c, conn, user, referral):
    c.execute('update referrals set attached_referrals = %s where user = %s', (referral, user))
    conn.commit()


def update_referral_bonus(current_user, payment_sum):
    con = mysql_connection()
    cur = con.cursor()
    referral = get_referral(current_user)[0]
    bonus = round(payment_sum * 0.4, 2)
    user_id = fetch_user_referral(referral)[0]
    cur.execute('update referrals set bonus_balance = bonus_balance + %s where user = %s', (bonus, user_id))
    con.commit()
    con.close()


def check_referral(user_id):
    connection = mysql_connection()
    curs = connection.cursor()
    curs.execute('select attached_referrals from referrals where user = %s', (user_id, ))
    result = curs.fetchone()[0]
    connection.close()
    if result:
        return True


def is_valid(link):
    conn = mysql_connection()
    c = conn.cursor()
    c.execute('select user from referrals where referral = %s', (link,))
    res = c.fetchall()
    conn.close()
    if len(res) == 0:
        return False
    else:
        return True

