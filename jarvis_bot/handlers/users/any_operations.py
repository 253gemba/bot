from aiogram import types
from aiogram.dispatcher import FSMContext

from data import config
from keyboards.default import default_keyboards, default_buttons
from loader import dp, bot
from utils.db_api.python_mysql import mysql_connection
from utils.default_tg.default import get_user_menu


@dp.message_handler(lambda message: message.text == default_buttons.button_cancel_operation.text or
                                    message.text == default_buttons.button_main_menu.text or
                                    message.text == default_buttons.button_close_profile.text,
                    content_types="any", state="*")
async def any_messages(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    msg_text = str(message.text)
    conn = mysql_connection()
    c = conn.cursor(buffered=True)
    state_data = await state.get_data()
    state_state = await state.get_state()
    await state.finish()
    if msg_text == default_buttons.button_cancel_operation.text and 0:
        await state.finish()
        await bot.send_message(user_id,
                               'Операция отменена',
                               reply_markup=get_user_menu(c, user_id))
    elif msg_text in (default_buttons.button_main_menu.text, default_buttons.button_cancel_operation.text,
                      default_buttons.button_close_profile.text):
        await bot.send_message(user_id,
                               '✨ Вернулись в главное меню\n\n'
                               f'<b>/{config.COMMANDS[0][0]}</b> - найти объявление\n'
                               f'<b>/{config.COMMANDS[1][0]}</b> - подать объявление\n'
                               f'<b>/{config.COMMANDS[2][0]}</b> - настроить оповещения\n'
                               f'<b>/{config.COMMANDS[3][0]}</b> - изменить город, баланс\n'
                               f'<b>/{config.COMMANDS[4][0]}</b> - задать вопрос',
                               reply_markup=get_user_menu(c, user_id))
    else:
        await state.finish()
        await bot.send_message(user_id,
                               f'Не могу распознать Вашу команду :(',
                               reply_markup=get_user_menu(c, user_id))
    c.close()
    conn.close()
