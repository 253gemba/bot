from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from keyboards.inline import dynamic_keyboards
from loader import dp
from utils.db_api.python_mysql import mysql_connection


@dp.message_handler(CommandHelp(), state="*")
async def bot_help(message: types.Message):
    # text = ("Список команд: ",
    #         "/start - Начать диалог",
    #         "/help - Получить справку")
    #
    # await message.answer("\n".join(text))

    conn = mysql_connection()
    c = conn.cursor(buffered=True)
    for old_param_id, now_param_id in [[None, 1], [1, 2]]:
        inline_kb = await dynamic_keyboards.get_ad_param_keyboard(c, now_param_id, 343, old_param_id=old_param_id,
                                                                  page=0)
        c.execute("select param_question, is_required from category_params where param_id = %s",
                  (now_param_id,))
        param_question, is_required = c.fetchone()
        add_text = f'\n\n<i>* это не обязательный параметр и Вы можете пропустить его выбор</i>' if not \
            is_required else ''
        await message.answer(text=f'<b>{param_question}</b>'
                                     f'{add_text}',
                                reply_markup=inline_kb)
