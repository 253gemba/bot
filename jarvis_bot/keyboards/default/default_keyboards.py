from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

from keyboards.default.default_buttons import *

admin_result = ReplyKeyboardMarkup(resize_keyboard=True)
edit_personnel_menu = ReplyKeyboardMarkup(resize_keyboard=True)
cancel_operation_menu = ReplyKeyboardMarkup(resize_keyboard=True)
cancel_operation_menu.row(button_cancel_operation)

# стоимость товара
ad_price_menu = ReplyKeyboardMarkup(resize_keyboard=True)
ad_price_menu.row(button_back, button_reset_ad)

# загрузка фото
load_photo_menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
load_photo_menu.row(button_continue)
load_photo_menu.row(button_back, button_reset_ad)

# меню курьера
courier_menu = ReplyKeyboardMarkup(resize_keyboard=True)
courier_menu.row(button_my_balance, button_share_geo)
courier_menu.row(button_all_orders, button_in_progress)

# меню пользователя
user_menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
user_menu.row(button_find_ads, button_add_ad)
user_menu.row(button_my_ads, button_my_profile)
user_menu.row(button_help)

# skip menu
skip_menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
skip_menu.row(button_skip)
skip_menu.row(button_back, button_reset_ad)

# skip menu
back_reset_menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
back_reset_menu.row(button_back, button_reset_ad)

# мой лк
my_profile_menu = ReplyKeyboardMarkup(resize_keyboard=True)
my_profile_menu.row(button_my_balance, button_change_city)
my_profile_menu.row(button_my_ads, button_notifications)
my_profile_menu.row(button_referral, button_attach_ref, button_favourites)
my_profile_menu.row(button_close_profile)


# go to head menu
go_to_head_menu = ReplyKeyboardMarkup(resize_keyboard=True)
go_to_head_menu.row(button_main_menu)

# рассылка
mailing_menu = ReplyKeyboardMarkup(resize_keyboard=True)
# mailing_menu.row(button_mail_text, button_mail_media)
# mailing_menu.row(button_mail_button, button_mail_preview)
# mailing_menu.row(button_mail_see_delayed, button_mail_do_delay)
mailing_menu.row(button_main_menu, button_mail_start)

# сегментированная рассылка
mail_segment_menu = ReplyKeyboardMarkup(resize_keyboard=True)
mail_segment_menu.row(button_mailing_segment_all, button_main_menu)

# поделиться номером
share_phone_menu = ReplyKeyboardMarkup(resize_keyboard=True)
share_phone_menu.row(button_share_phone)

# меню аналитики
analytics_menu = ReplyKeyboardMarkup(resize_keyboard=True)
analytics_menu.row(button_find_users, button_get_db)
analytics_menu.row(button_main_menu)

# меню администратора
admin_menu = ReplyKeyboardMarkup(resize_keyboard=True)
admin_menu.row(button_personnel, button_analytics)
admin_menu.row(button_new_mailing, button_all_orders)
admin_menu.row(button_in_progress, button_not_assigned)
admin_menu.row(button_create_order)


# меню выбора геопозиции
def select_geo(is_edit=0):
    select_geo_menu = ReplyKeyboardMarkup(resize_keyboard=True)
    select_geo_menu.row(button_send_geo_hand)
    select_geo_menu.row(button_send_geo_auto)
    if is_edit:
        select_geo_menu.row(button_main_menu)
    return select_geo_menu


def withdraw_balance(balance):
    reply_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    reply_kb.row(KeyboardButton(text=f'{balance}'))
    reply_kb.row(button_cancel_operation)
    return reply_kb


def share_phone_username(username):
    reply_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    reply_kb.insert(f'@{username}' if username else '')
    reply_kb.insert(button_share_phone)
    reply_kb.row(button_back, button_reset_ad)
    return reply_kb


def get_buttons_text_from_menu(need_menu):
    buttons_text = list()
    for one_line in need_menu.keyboard:
        for one_button in one_line:
            buttons_text.append(one_button.text)
    return buttons_text
