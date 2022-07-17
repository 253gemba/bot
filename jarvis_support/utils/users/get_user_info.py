from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def get_info_user(c, find_user_id):
    c.execute("select full_name, phone_number, is_black "
              "from users where user_id = %s", (find_user_id,))
    full_name, phone_number, is_black = c.fetchone()
    c.execute("select count(*) from client_users where user_id = %s", (find_user_id,))
    is_client = c.fetchone()[0]
    return_text = f"<b>👤 {full_name}</b>\n" \
                  f"<b>📞 Телефон:</b> {phone_number}\n" \
                  f"<b>Клиент:</b> {'✔' if is_client else '🔴'}\n" \
                  f"<b>BL:</b> {'активен ✔' if not is_black else 'в черном списке 🔴'}"
    inline_kb = InlineKeyboardMarkup(row_width=2)
    inline_kb.insert(InlineKeyboardButton(text=f'Заблокировать 🔒' if not is_black else 'Разблокировать 🔓',
                                          callback_data=f'editBlackUser_{find_user_id}'))
    inline_kb.insert(InlineKeyboardButton(text=f'Боты 🤖' if is_client else '',
                                          callback_data=f'userBots_{find_user_id}'))
    inline_kb.row(InlineKeyboardButton(text=f'Закрыть меню ✖',
                                       callback_data=f'hide'))
    return return_text, inline_kb
