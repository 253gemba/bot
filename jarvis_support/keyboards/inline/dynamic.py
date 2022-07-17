import datetime
import math

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


async def delete_element(query=None, is_delete=1):
    inline_kb = InlineKeyboardMarkup()
    inline_kb.row(InlineKeyboardButton(text=f'Удалить' if is_delete else '',
                                       callback_data=f'{query}_1'),
                  InlineKeyboardButton(text=f'{"Отмена" if is_delete else "Скрыть"} ✖',
                                       callback_data=f'hide'))
    return inline_kb


def now_date_kb():
    reply_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    now_datetime = datetime.datetime.now()
    reply_kb.insert(KeyboardButton(f'{now_datetime.year}-{now_datetime.month}-{now_datetime.day}'))
    return reply_kb


async def get_commands_menu(c, page=0):
    page = int(page)
    inline_kb = InlineKeyboardMarkup(row_width=2)
    c.execute("select command_id, command_name from commands")
    all_dumps = c.fetchall()
    offset = 10
    for one_command in all_dumps[offset * page:offset * (page + 1)]:
        command_id, command_name = one_command
        inline_kb.insert(InlineKeyboardButton(text=f'{command_name}',
                                              callback_data=f'editCommand_{command_id}'))
    count_pages = math.ceil(len(all_dumps) / offset)
    if count_pages > 1:
        inline_kb.row(InlineKeyboardButton(text=f'<<' if page > 0 else '',
                                           callback_data=f'commandsPage_{page - 1}'),
                      InlineKeyboardButton(text=f'{page + 1}/{count_pages}',
                                           callback_data=' '),
                      InlineKeyboardButton(text=f'>>' if len(all_dumps) > (page + 1) * offset else '',
                                           callback_data=f'commandsPage_{page + 1}'))
    inline_kb.row(InlineKeyboardButton(text=f'➕ Добавить',
                                       callback_data=f'addCommand'))
    return inline_kb


async def edit_command_menu(c, command_id):
    inline_kb = InlineKeyboardMarkup(row_width=2)
    c.execute("select command_id, command_name from commands where command_id = %s",
              (command_id,))
    inline_kb.insert(InlineKeyboardButton(text=f'Изм. команду',
                                          callback_data=f'editCommandName_{command_id}'))
    inline_kb.insert(InlineKeyboardButton(text=f'Изм. описание',
                                          callback_data=f'editCommandDescription_{command_id}'))
    inline_kb.insert(InlineKeyboardButton(text=f'Изм. ответ',
                                          callback_data=f'editCommandAnswer_{command_id}'))
    inline_kb.row(InlineKeyboardButton(text=f'↩ Вернуться к командам',
                                       callback_data=f'commandsPage_{0}'))
    return inline_kb
