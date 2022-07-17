from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

from keyboards.default.default_buttons import *


# пользовательские
admin_result = ReplyKeyboardMarkup(resize_keyboard=True)
user_menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
admin_menu = ReplyKeyboardMarkup(resize_keyboard=True)
client_menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

# разделы
dispatcher_menu = ReplyKeyboardMarkup(resize_keyboard=True)
edit_personnel_menu = ReplyKeyboardMarkup(resize_keyboard=True)
mailing_menu = ReplyKeyboardMarkup(resize_keyboard=True)
payments_menu = ReplyKeyboardMarkup(resize_keyboard=True)

# вспомогательные
cancel_operation_menu = ReplyKeyboardMarkup(resize_keyboard=True)
share_phone_menu = ReplyKeyboardMarkup(resize_keyboard=True)
mail_segment_menu = ReplyKeyboardMarkup(resize_keyboard=True)
sources_accept_menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
server_ip_menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

# отмена операции
cancel_operation_menu.row(button_cancel_operation)

# is sources
sources_accept_menu.insert(button_yes)
sources_accept_menu.insert(button_no)

# рассылка
mailing_menu.row(button_mail_text, button_mail_media)
mailing_menu.row(button_mail_button, button_mail_preview)
mailing_menu.row(button_mail_see_delayed, button_mail_do_delay)
mailing_menu.row(button_main_menu, button_mail_start)

# сегментированная рассылка
mail_segment_menu.row(button_segment_users, button_segment_clients)
mail_segment_menu.row(button_segment_all, button_main_menu)

# поделиться номером
share_phone_menu.row(button_share_phone)

# меню администратора
admin_menu.row(button_commands, button_new_mailing)
admin_menu.row(button_payments, button_stats)

# меню с пользователями
edit_personnel_menu.row(button_find_users)
edit_personnel_menu.row(button_main_menu)


def get_buttons_text_from_menu(need_menu):
    buttons_text = list()
    for one_line in need_menu.keyboard:
        for one_button in one_line:
            buttons_text.append(one_button.text)
    return buttons_text
