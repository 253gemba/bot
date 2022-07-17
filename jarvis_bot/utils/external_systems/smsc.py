import requests


async def send_sms(phone, text):
    login = 'kisel007'
    password = 'iPXXp4X4E2z32bb'
    return requests.post(
        f"https://smsc.ru/sys/send.php?login={login}&psw={password}&phones={phone}&mes={text}")
