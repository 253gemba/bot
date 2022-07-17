from aiogram import types
from aiogram.dispatcher import FSMContext
from mysql.connector import MySQLConnection

from keyboards.default import default_keyboards
from keyboards.inline.dynamic import edit_command_menu
from loader import dp, bot
from states.states import *
from utils.db_api.python_mysql import read_db_config
from utils.fast_answers.commands import get_command_info, update_commands
from utils.telegram_functions.telegram_work import get_message_type


@dp.message_handler(state=CreateCommand.states, content_types=types.ContentType.ANY)
async def process_create_command(message: types.Message, state: FSMContext):
    print(message)
    user_id = message.from_user.id
    msg_text = str(message.text)
    # CONNECT TO DATABASE
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    c = conn.cursor(buffered=True)
    now_state = await state.get_state()
    now_data = await state.get_data()
    print(f'process_find_user: {user_id}; {msg_text}')
    try:
        command_id = now_data['command_id']
    except:
        command_id = 0
    if not command_id:
        if CreateCommand.command_name.state == now_state:
            msg_text = msg_text.replace("/", "")
            if len(msg_text.replace("_", "")) and msg_text.replace("_", "").isalpha() and " " not in msg_text:
                await state.update_data(command_name=msg_text)
                await CreateCommand.next()
                await bot.send_message(user_id,
                                       f'Введите <b>описание команды</b>\n\n'
                                       f'💡 <i>Описание - это то, что увидит менеджер, отвечая на вопрос в '
                                       f'комментариях. Пользователь описание не видит</i>')
            else:
                await bot.send_message(user_id,
                                       f'⚠ Название должно состоять только из латинских букв и знаков нижнего '
                                       f'подчеркивания (необяз.)')
        elif CreateCommand.command_description.state == now_state:
            if len(msg_text) < 256:
                await state.update_data(command_description=msg_text)
                await CreateCommand.next()
                await bot.send_message(user_id,
                                       f'Отправьте <b>контент команды</b>\n\n'
                                       f'💡 <i>Контент - это то, что увидит пользователь. Текст, фото, видео, '
                                       f'голос - всё, что угодно. Длина текста до 4096 символов</i>')
            else:
                await bot.send_message(user_id,
                                       f'⚠ Длина описания не должна превышать 256 символов. '
                                       f'Укоротите и повторите попытку')
        elif CreateCommand.command_content.state == now_state:
            if len(msg_text) < 4096:
                command_name = now_data['command_name']
                command_description = now_data['command_description']
                content_media_type, content_media_id, content_media_text = await get_message_type(message)
                c.execute("insert into commands (command_name, command_description, content_media_id, "
                          "content_media_type, content_media_text) "
                          "values (%s, %s, %s, %s, %s)",
                          (command_name, command_description, content_media_id, content_media_type, content_media_text))
                conn.commit()
                command_id = c.lastrowid
                await state.finish()
                await bot.send_message(user_id,
                                       f'Команда успешно создана ✅',
                                       reply_markup=default_keyboards.admin_menu)
                await get_command_info(c, command_id, user_id,
                                       inline_kb=await edit_command_menu(c, command_id))
            else:
                await bot.send_message(user_id,
                                       f'⚠ Длина контента не должна превышать 4096 символов. '
                                       f'Укоротите и повторите попытку')
    else:
        is_accept = 1
        if now_state == CreateCommand.command_name.state:
            msg_text = msg_text.replace("/", "")
            if len(msg_text.replace("_", "")) and msg_text.replace("_", "").isalpha() and " " not in msg_text:
                c.execute("update commands set command_name = %s where command_id = %s",
                          (msg_text, command_id))
                conn.commit()
            else:
                is_accept = 0
                await bot.send_message(user_id,
                                       f'⚠ Название должно состоять только из латинских букв и знаков нижнего '
                                       f'подчеркивания (необяз.)')
        if now_state == CreateCommand.command_description.state:
            if len(msg_text) < 256:
                c.execute("update commands set command_description = %s where command_id = %s",
                          (msg_text, command_id))
                conn.commit()
            else:
                is_accept = 0
                await bot.send_message(user_id,
                                       f'⚠ Длина описания не должна превышать 256 символов. '
                                       f'Укоротите и повторите попытку')
        if now_state == CreateCommand.command_content.state:
            if len(msg_text) < 4096:
                content_media_type, content_media_id, content_media_text = await get_message_type(message)
                print(content_media_type, content_media_id, content_media_text, command_id)
                c.execute("update commands set content_media_id = %s, content_media_type = %s, content_media_text = %s "
                          "where command_id = %s",
                          (content_media_id, content_media_type, content_media_text, command_id))
                conn.commit()
            else:
                is_accept = 0
                await bot.send_message(user_id,
                                       f'⚠ Длина контента не должна превышать 4096 символов. '
                                       f'Укоротите и повторите попытку')
        if is_accept:
            await state.finish()
            await bot.send_message(user_id,
                                   f'✅ Успешно изменено',
                                   reply_markup=default_keyboards.admin_menu)
            await get_command_info(c, command_id, user_id,
                                   inline_kb=await edit_command_menu(c, command_id))
    await update_commands(c)
    c.close()
    conn.close()
