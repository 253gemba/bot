from aiogram.types import KeyboardButton

# SHARE PHONE / GEO
button_share_phone = KeyboardButton("📱 Поделиться номером", request_contact=True)
# сегменты рассылки
button_segment_clients = KeyboardButton("Клиенты")
button_segment_users = KeyboardButton("Пользователи")
button_segment_all = KeyboardButton('По всем ⏺')
# yes/no
button_yes = KeyboardButton('Да')
button_no = KeyboardButton('Нет')
# cancel
button_cancel_operation = KeyboardButton('Отменить')
# ADMIN BUTTONS
# ----------
button_commands = KeyboardButton(f'Команды 🤖')
button_payments = KeyboardButton('Платежи 💸')
button_stats = KeyboardButton('Статистика 📊')
# --- PEOPLES
button_find_users = KeyboardButton(f'Пользователи 🔎')
# ----------
button_to_admin = KeyboardButton('Панель администратора 👨‍💻')
button_to_user = KeyboardButton('Панель пользователя 👨‍🦰')
# MAIL BUTTONS
button_new_mailing = KeyboardButton('Рассылка ✉')
button_mailing_text = KeyboardButton('Текст 📋')
button_mail_media = KeyboardButton('Медиа 🗻')
button_mail_button = KeyboardButton('Кнопки 🔘')
button_mail_text = KeyboardButton('Текст 📝')
button_mail_preview = KeyboardButton('Предпросмотр 🗽')
button_mail_do_delay = KeyboardButton('Отложить ⏱')
button_mail_see_delayed = KeyboardButton('Отложка ⌚')
button_mail_start = KeyboardButton('Разослать 🚀')
button_main_menu = KeyboardButton('Главное меню 🏠')
