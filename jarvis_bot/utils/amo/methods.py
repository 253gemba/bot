from amocrm.v2 import Lead as _Lead, custom_field, Contact as _Contact
from amocrm.v2 import tokens, Lead
from mysql.connector import MySQLConnection

from data import config
from utils.db_api.python_mysql import read_db_config


class Lead(_Lead):
    city = custom_field.TextCustomField(u'Город')
    address = custom_field.TextCustomField(u"Адрес")
    service = custom_field.TextCustomField(u"Услуга")
    start_datetime = custom_field.DateTimeCustomField(u"Начало")
    count_loaders = custom_field.NumericCustomField(u"Кол-во грузчиков")
    car_type = custom_field.TextCustomField(u"Авто")
    minimum = custom_field.NumericCustomField(u"Минималка Грузчики")
    min_auto = custom_field.TextCustomField(u"Минималка Авто")
    floor_descent = custom_field.TextCustomField(u"Этажи Спуск")
    floor_rise = custom_field.TextCustomField(u"Этажи Подъем")
    rigging = custom_field.TextCustomField(u"Такелаж")
    add_service = custom_field.MultiSelectCustomField(u"Доп Услуги")
    area_price = custom_field.NumericCustomField(u"Пригород/Межгород")
    note = custom_field.TextCustomField(u"Примечание")
    add_hour = custom_field.TextCustomField(u"Доп час")
    paid_for_km = custom_field.TextCustomField(u"Допплата за км")


class Contact(_Contact):
    phone = custom_field.TextCustomField(u'Телефон')


class AmoMethods():
    def __init__(self, client_id, client_secret, subdomain, redirect_url, code):
        self.client_id = client_id
        self.client_secret = client_secret
        self.subdomain = subdomain
        self.redirect_url = redirect_url
        self.storage = tokens.FileTokensStorage()
        tokens.default_token_manager(
            client_id=client_id,
            client_secret=client_secret,
            subdomain=subdomain,
            redirect_url=redirect_url,
            storage=tokens.FileTokensStorage(),  # by default FileTokensStorage
        )
        tokens.default_token_manager.init(code=code, skip_error=True)

    def custom_fields_generator(self, all_fields):
        custom_fields_values = list()
        for one_field in all_fields:
            if one_field[1]:
                custom_fields_values.append(
                    {
                        "field_id": one_field[0],  # телефон
                        "values": [
                            {
                                "value": str(one_field[1])
                            }
                        ]
                    }
                )
        return custom_fields_values

    def get_all_deals(self):
        leads = Lead.objects.filter(query='заказ оформлен')
        return leads

    def get_rejected_deals(self):
        leads_rejected = Lead.objects.filter(query='думает - узнал решение') + Lead.objects.filter(query='отказ')
        return leads_rejected

    def send_comment(self, deal_id, msg_text):
        # CONNECT TO DATABASE
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        c = conn.cursor(buffered=True)
        comment_text = msg_text
        deal_crm_id = None
        find_order = Lead.objects.get(object_id=deal_crm_id)
        note = find_order.notes.objects.create(text=comment_text, note_type='common')
        conn.commit()
        c.close()
        conn.close()

    def update_status(self, deal_id, status_id):
        """
        param: status_id: 34446823 - исп назначены
        param: status_id: 34300909 - начали работу
        param: status_id: 34302931 - поиск исполнителей
        """
        order = Lead.objects.get(object_id=deal_id)
        print(order)
        order.status = status_id
        order.save()


amo_methods = AmoMethods(
    client_id=config.AMO_CLIENT_ID,
    client_secret=config.AMO_CLIENT_SECRET,
    subdomain=config.AMO_SUBDOMAIN,
    redirect_url=config.AMO_REDIRECT_URI,
    code=config.AMO_CODE
)
