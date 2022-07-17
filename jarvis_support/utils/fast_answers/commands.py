from aiogram.types.bot_command import BotCommand
from aiogram.types.bot_command_scope import BotCommandScopeChat
from aiogram.types.inline_keyboard import InlineKeyboardMarkup

from loader import bot
from utils.telegram_functions.telegram_work import send_message_user


async def update_commands(c):
    c.execute("select command_name, command_description from commands")
    commands_db = c.fetchall()
    c.execute("select chat_id from channels_and_chats")
    chats = c.fetchall()
    commands = []
    for one_command in commands_db:
        commands.append(BotCommand(command=one_command[0],
                                   description=one_command[1]))
    for one_chat in chats:
        scope = BotCommandScopeChat(chat_id=one_chat[0])
        await bot.delete_my_commands(scope=scope)
        await bot.set_my_commands(commands=commands,
                                  scope=scope)


async def get_command_info(c, command_id, user_id, with_content=0, inline_kb: InlineKeyboardMarkup = None):
    c.execute("select command_name, command_description, content_media_id, content_media_type, content_media_text "
              "from commands where command_id = %s", (command_id,))
    command_name, command_description, content_media_id, content_media_type, content_media_text = c.fetchone()
    if with_content:
        await send_message_user(user_id,
                                content_media_text,
                                content_media_type,
                                content_media_id,
                                inline_buttons=None if not inline_kb else inline_kb.inline_keyboard)
    else:
        await send_message_user(user_id,
                                f'<b>Команда /{command_name}</b>\n\n'
                                f'<b>Описание:</b> {command_description}',
                                None,
                                None,
                                inline_buttons=None if not inline_kb else inline_kb.inline_keyboard)
