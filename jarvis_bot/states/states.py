from aiogram.dispatcher.filters.state import StatesGroup, State


class SendGeo(StatesGroup):
    geo_map = State()


class CreateAd(StatesGroup):
    photo = State()
    description = State()
    contact_method = State()
    price = State()


class CreateFind(StatesGroup):
    edit_options = State()


class AddInformation(StatesGroup):
    info_values = State()


class AddMoney(StatesGroup):
    money = State()


class SendMessage(StatesGroup):
    message_content = State()


class Mailing(StatesGroup):
    message_id = State()
    accept_mailing = State()


class SetCity(StatesGroup):
    area = State()
    city = State()


class MakeWithdraw(StatesGroup):
    amount = State()
