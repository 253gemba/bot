from utils.db_api.python_mysql import mysql_connection


def is_exist(user_id):
    conn = mysql_connection()
    c = conn.cursor()
    c.execute("select user_id from partnership where user_id = %s", (user_id,))
    res = c.fetchone()
    conn.close()
    if res is None:
        return False
    return True


