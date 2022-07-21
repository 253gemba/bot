from aiogram.types import KeyboardButton

# SHARE PHONE / GEO
button_share_phone = KeyboardButton("📱 Поделиться номером", request_contact=True)
button_share_geo = KeyboardButton("📍 Поделиться геопозицией")
# отделы
button_mailing_segment_all = KeyboardButton('По всем ⏺')
button_skip = KeyboardButton('Пропустить ⏩')
button_continue = KeyboardButton('Продолжить ⏩')
button_back = KeyboardButton('↩ Назад')
button_reset_ad = KeyboardButton('🔄 Сбросить')
# пользователи
button_cancel_operation = KeyboardButton('Отменить ❌')
# мой лк
button_my_balance = KeyboardButton('💰 Баланс')
button_change_city = KeyboardButton('📍 Сменить город')
# ПОЛЬЗОВАТЕЛЬ
button_find_ads = KeyboardButton('🔎 Поиск')
button_add_ad = KeyboardButton('➕ Новое объявление')
button_my_ads = KeyboardButton('📝 Мои объявления')
button_favourites = KeyboardButton('🗂 Избранное')
button_referral = KeyboardButton('🤝 Партнерская программа')
button_attach_ref = KeyboardButton('🔗 Прикрепить ссылку')
button_notifications = KeyboardButton('🔔 Уведомления')
button_my_profile = KeyboardButton('😎 Профиль')
button_help = KeyboardButton('❓ Задать вопрос')
button_send_geo_hand = KeyboardButton('👆 Вручную')
button_send_geo_auto = KeyboardButton('📍 Автоматически', request_location=True)
# ADMIN BUTTONS
# ----------
button_personnel = KeyboardButton(f'Люди 👥')
button_analytics = KeyboardButton(f'Данные 🗂')
button_find_users = KeyboardButton(f'Пользователи 🔎')
button_all_orders = KeyboardButton('Все заказы 📝')
button_in_progress = KeyboardButton('В исполнении ⏱')
button_not_assigned = KeyboardButton('Неназначенные 🤷‍♂')
button_get_db = KeyboardButton('База данных 👥')
button_create_order = KeyboardButton('Добавить заказ ➕')
button_stats = KeyboardButton('Статистика 📊')
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
button_close_profile = KeyboardButton('Закрыть раздел профиль ✖')
# segment mailing
button_mail_start_25 = KeyboardButton(f'25 %')
button_mail_start_50 = KeyboardButton(f'50 %')
button_mail_start_75 = KeyboardButton(f'75 %')
button_mail_start_100 = KeyboardButton(f'100 %')
