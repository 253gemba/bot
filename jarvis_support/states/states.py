from aiogram.dispatcher.filters.state import StatesGroup, State


class Mailing(StatesGroup):
    wait_mail_text = State()
    wait_mail_media = State()
    delay_mail = State()
    mail_button_text = State()
    mail_button_link = State()


class CreateCommand(StatesGroup):
    command_name = State()
    command_description = State()
    command_content = State()


class CreateBot(StatesGroup):
    name = State()
    username = State()
    service_date = State()
    server_date = State()
    service_payment = State()
    server_payment = State()
    screen = State()
    main_file = State()
    is_source = State()
    source_ip = State()
    source_folder = State()
    source_database = State()
    database_login = State()
    database_password = State()


class Payments(StatesGroup):
    amount = State()
    description = State()


class SendMessage(StatesGroup):
    message_content = State()


class EditUser(StatesGroup):
    department = State()


class FindReference(StatesGroup):
    query = State()


class FindUser(StatesGroup):
    user_id = State()


class Registration(StatesGroup):
    full_name = State()
    phone_number = State()
    company_departament = State()
