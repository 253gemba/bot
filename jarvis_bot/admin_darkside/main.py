import asyncio
import logging
import os
from datetime import timedelta

import requests
from aiogram import Bot, types
from flask import Flask, render_template, redirect, url_for, request, abort
from flask_httpauth import HTTPBasicAuth
from flask_wtf import FlaskForm
from sqlalchemy.engine import CursorResult
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, IntegerField, FileField, SelectField, widgets, BooleanField, TextAreaField, \
    DateTimeField, SelectMultipleField, MultipleFileField
from wtforms.validators import DataRequired

import config
from data import db_session
from data.__all_models import *
from forms import UsersForm, PaymentsForm, UtmForm

bot = Bot(token="1728753183:AAGDN3BDkSa7g2BU7Zu5LDN7bcZM69MahEA", parse_mode=types.ParseMode.HTML)

UPLOAD_FOLDER = 'static/img'
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
auth = HTTPBasicAuth()

users = {
    "grunt_180": generate_password_hash("hh45Bm12fG")
}

cats = {
    'ads': [Ads, 'ad_id', 'Объявления пользователей', 'объявления',
            ["ID", "Раздел", "Категория", "Описание", "TG ID", "Стоимость, руб", "Тариф, руб", "Дата закрытия",
             "Жалоба", "Управление"]],
    'head_categories': [Categories, 'category_id', 'Разделы', 'категории',
                        ["ID", "Название", "15 дн, объявления", "30 дн, объявления",
                         "15 дн, уведомления", "30 дн, уведомления"]],
    'categories': [Categories, 'category_id', 'Категории и разделы', 'категории',
                   ["ID", "Название"]],
    'category_params': [CategoryParams, 'brand_id', 'Параметры категорий', 'параметра категории',
                        ["ID", "Бренд", "Управление"]],
    'param_options': [ParamOptions, 'option_id', 'Модели категории', 'модели категории',
                      ["ID", "Название", "Управление"]],
    'options': [ParamOptions, 'option_id', 'Модели категории', 'модели категории',
                ["ID", "Название", "Управление"]],
    'param_brand_options': [ParamOptions, 'option_id', 'Модели категории', 'модели категории',
                            ["ID", "Параметр", "Значение", "Управление"]],
    'payments': [Payments, 'payment_id', 'Платежи', 'платежа',
                 ["ID", "TG ID", "Дата и время", "Статус", "Сумма, руб.", "ID в платежке", "Город", "Управление"]],
    'users': [Users, 'user_id', 'Пользователи бота', 'пользователя бота',
              ["TG ID", "Зарегистрирован", "Имя", "Фамилия", "@username", "Живой", "Блокировка",
               "Баланс", "Количество объявлений", "Сумма пополнений", "Город", "Управление"]],
    'all_cities': [Cities, 'city_id', 'Города, края, области', 'города',
                   ["ID", "Область/край/республика", "Пользователи", "Сумма пополнений"]],
    'stats': [Stats, 'city_id', 'ТОП-50 городов', 'города',
              ["ID города", "Пользователи", "Название города", "Сумма пополнений, руб", "Управление"]],
    'mailing': [Mailing, 'mail_id', 'Рассылки', 'рассылки',
                ["ID", "Дата и время", "Рассылку получили", "Текст рассылки", "Управление"]],
    'utm': [Utm, 'utm_id', 'UTM-ссылки', 'ссылки',
            ["ID", "Дата и время создания", "Бонус", "Переходы", "Ссылка", "Управление"]],
    'ads_photos': [AdsPhotos, 'utm_id', 'UTM-ссылки', 'ссылки',
                   ["ID", "Дата и время создания", "Бонус", "Переходы", "Ссылка", "Управление"]],
    'brands_photos': [BrandsPhotos, 'utm_id', 'UTM-ссылки', 'ссылки',
                      ["ID", "Дата и время создания", "Бонус", "Переходы", "Ссылка", "Управление"]],
    'brand_params': [BrandParams, 'brand_param_id', 'Параметры модели', 'параметра модели',
                     ["ID", "Дата и время создания", "Бонус", "Переходы", "Ссылка", "Управление"]],
    'lists': [Params, 'param_id', 'Параметры категорий', 'параметра категории',
              ["ID", "Название", "Тип", "Вопрос", "Управление"]],
    'closes_types': [ClosesTypes, 'type_id', 'Название', 'Часть тела',
              ["ID", 'Название', 'Часть тела', 'Вид одежды', 'Управление']],
    'withdrawal': [Withdrawal, 'id', ['ID Телеграм', 'Пользователь', 'Номер карты', 'Сумма',
                                      'Дата создания', 'Управление']]
}


def generate_forms(**kwargs):
    session = db_session.create_session()

    class MultiCheckboxField(SelectMultipleField):
        widget = widgets.ListWidget(prefix_label=False)
        option_widget = widgets.CheckboxInput()

    class WithdrawalsForm(FlaskForm):
        id = TextAreaField('Идентификатор записи')
        tg_user = TextAreaField('Пользователь телеграм')
        card_num = IntegerField('Номер банковской карты')
        created_date = DateTimeField(label='Время создания', format='%d.%m.%Y %H:%M',
                                     default=datetime.utcnow() + timedelta(hours=3))

    class MailingForm(FlaskForm):
        mail_datetime = DateTimeField(label='Дата и время рассылки', format='%d.%m.%Y %H:%M',
                                      default=datetime.utcnow() + timedelta(hours=3))
        mail_text = TextAreaField('Текст. Поддерживаются теги <b>жирный</b>, <i>курсив</i>')
        mail_photo = FileField(label='Фото или видео')
        all_areas = []
        t = []
        for x in session.query(Cities).order_by(Cities.city_area).all():
            if x.city_area not in t:
                t.append(x.city_area)
                all_areas.append([x.city_id, x.city_area])
        all_categories = dict(all_areas)
        all_cities = {'Вся Россия': [[0, 'Вся Россия']]}
        for item in all_areas:
            results = session.query(Cities).filter(Cities.city_area == item[1]).order_by(Cities.city_name).all()
            all_cities[item[1]] = [[f"obl{item[0]}", f"{item[1]}"]]
            for result in results:
                if item[1] not in all_cities.keys():
                    all_cities[item[1]] = [[result.city_id, result.city_name]]
                else:
                    old_dict = all_cities[item[1]]
                    old_dict.append([result.city_id, result.city_name])
                    all_cities[item[1]] = old_dict

        city_id = SelectField('Выберите город',
                              choices=all_cities,
                              coerce=str,
                              default=0)

    class CategoriesForm(FlaskForm):
        category_name = StringField('Название категории', validators=[DataRequired()])
        all_categories = [[x.category_id, x.category_name] for x in
                          session.query(Categories).filter(Categories.parent_id == None).all()]
        all_categories.insert(0, [None, "Это главная категория"])
        all_categories = dict(all_categories)
        parent_id = SelectField('Основная категория (если это подкатегория)',
                                choices=all_categories.items(),
                                widget=widgets.Select(), default=None)
        photo = FileField('Фото товара по умолчанию')
        tariff_first_price = IntegerField('Цена объявлений 15 дней', validators=[DataRequired()])
        tariff_second_price = IntegerField('Цена объявлений 30 дней', validators=[DataRequired()])
        tariff_notify_first = IntegerField('Цена уведомлений 15 дней', validators=[DataRequired()])
        tariff_notify_second = IntegerField('Цена уведомлений 30 дней', validators=[DataRequired()])

    class AdForm(FlaskForm):
        all_categories = [[x.category_id, x.category_name] for x in
                          session.query(Categories).filter(Categories.parent_id == None).all()]
        all_categories.insert(0, [None, "Это главная категория"])
        all_categories = dict(all_categories)
        all_sections = [[x.category_id, x.category_name] for x in
                        session.query(Categories).filter(Categories.parent_id != None).all()]
        all_sections = dict(all_sections)
        category_id = SelectField('Раздел',
                                  choices=all_categories.items(),
                                  widget=widgets.Select(), default=None)
        section_id = SelectField('Категория',
                                 choices=all_sections.items(),
                                 widget=widgets.Select(), default=None)
        ad_price = IntegerField('Цена в объявлении')
        ad_description = TextAreaField('Описание')
        ad_contacts = TextAreaField('Контакты')
        date_close = DateTimeField('Дата закрытия', format='%d.%m.%Y %H:%M')
        is_paid = BooleanField('Оплачено?')
        is_warning = BooleanField('Есть жалобы?')

    class OptionsParams(FlaskForm):
        option_id = kwargs.get('option_id')
        if option_id:
            param_id = session.execute(f"select option_id from options "
                                       f"where param_id = {option_id}").scalar()
            all_parameters = session.execute(f"select param_id from options "
                                             f"where option_id = {option_id}").all()
            all_parameters: CursorResult
            new_items = []
            for row in all_parameters:
                new_items.append(row._asdict())
            all_parameters = new_items
            param_type = SelectField('Тип параметра', validators=[DataRequired()],
                                     choices=all_parameters.items())
        category_id = StringField('Значение',
                                  default=None)

    class OptionsForm(FlaskForm):
        option_name = StringField('Название',
                                  default=None)
        param_id = IntegerField('Параметр',
                                default=kwargs.get('param_id'))

    class BrandParamsForm(FlaskForm):
        brand_param_id = kwargs.get('brand_param_id')
        if brand_param_id:
            param_id, option_id = session.execute(f"select param_id, option_id from brand_params "
                                                  f"where brand_param_id = {brand_param_id}").first()
            param_name = session.execute(f"select param_name from params "
                                         f"where param_id = {param_id}").scalar()
            all_options = []
            for x in session.query(ParamOptions).filter(ParamOptions.param_id == param_id).all():
                all_options.append([x.option_id, x.option_name])
            param_id = SelectField('Параметр',
                                   default=param_name,
                                   choices=[[param_id, param_name]])
            option_id = SelectField('Значение',
                                    choices=all_options)
            photos = MultipleFileField('Фотографии')

    class ParamsForm(FlaskForm):
        param_name = StringField('Название',
                                 default=None)
        param_type = SelectField('Тип параметра', validators=[DataRequired()],
                                 choices=[['list', 'выбор из списка'],
                                          ['multilist', 'мультивыбор']])
        question_text = StringField('Вопрос пользователю',
                                    default=None)

    forms = {
        'ads': AdForm,
        'categories': CategoriesForm,
        'param_options': OptionsParams,
        'payments': PaymentsForm,
        'users': UsersForm,
        'all_cities': UsersForm,
        'mailing': MailingForm,
        'utm': UtmForm,
        'lists': ParamsForm,
        'options': OptionsForm,
        'brand_params': BrandParamsForm,
        'withdrawal': WithdrawalsForm
    }
    session.close()
    return forms


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


@app.route('/')
@app.route('/index')
@auth.login_required
def index():
    cat = request.args.get('cat', 'users')
    if cat not in cats.keys():
        abort(404)
    city_area = request.args.get('city_area')
    parent_id = request.args.get('parent_id')
    from_category = request.args.get('from_category')
    brand_id = request.args.get('brand_id')
    serial_id = request.args.get('serial_id')
    count_serials = 0
    model_id = request.args.get('model_id')
    param_id = request.args.get('param_id')
    option_id = request.args.get('option_id')
    is_warning = request.args.get("is_warning")
    set_category_id = request.args.get("set_category_id")
    closes_setting = request.args.get("closes_setting")
    is_clothes = 0
    if not is_warning:
        is_warning = 0
    session = db_session.create_session()
    category_name = cats[cat][2]
    if cat == 'categoriess':
        items = session.execute("select category_id, category_name, "
                                "IFNULL((select category_name from categories "
                                "where categories.category_id = m.parent_id), 'не найдена'), "
                                "tariff_first_price, tariff_second_price "
                                "from categories as m")
        items: CursorResult
        new_items = []
        for row in items:
            new_items.append(row._asdict())
        items = new_items
    elif cat == 'mailing':
        items = session.execute("select mail_id, mail_datetime, concat(count_people_get, '/', count_people_all), "
                                "concat(substr(mail_text, 1, 20), '...') "
                                "from mailing")
        items: CursorResult
        new_items = []
        for row in items:
            new_items.append(row._asdict())
        items = new_items

    elif cat == 'withdrawal':
        items = session.execute("select id, user_id, card_num, amount, created_date from withdrawal")
        items: CursorResult
        new_items = []
        for item in items:
            new_items.append(item._asdict())
        items = new_items
        category_name = f'Вывод средств'
    elif cat == 'stats':
        items = session.execute("select city_id, (select count(*) from users "
                                "where users.city_id = all_cities.city_id) as k, city_name, "
                                "(select sum(payment_amount) from payments "
                                "where payment_status = 'succeeded' and user_id in "
                                "(select user_id from users where users.city_id = all_cities.city_id)) "
                                "from all_cities order by k desc limit 50")
        items: CursorResult
        new_items = []
        for row in items:
            new_items.append(row._asdict())
        items = new_items
        count_users = session.query(Users).count()
        category_name = f'{category_name}.\n\n' \
                        f'Всего пользователей: {count_users}'
    elif cat == 'lists':
        if param_id:
            param_name = session.query(Params).filter(Params.param_id == param_id).scalar().param_name
            items = session.execute("select option_id, option_name "
                                    "from options where param_id = :param_id", {'param_id': param_id})
            category_name = f'Опции параметра "{param_name}"'
        else:
            items = session.execute("select param_id, param_name, "
                                    "IF(param_type = 'list', 'список', "
                                    "IF(param_type = 'multilist', 'мультисписок', "
                                    "IF(param_type = 'int', 'число', 'неизвестно'))), question_text "
                                    "from params "
                                    "where param_name <> 'Тариф'")
            category_name = f'Общий список параметров'
        items: CursorResult
        new_items = []
        for row in items:
            new_items.append(row._asdict())
        items = new_items
    elif cat == 'all_cities':
        from_days = request.args.get("from_days")
        if not from_days:
            from_days = 3000
        if not city_area:
            items = session.execute("select city_id, city_area as m, (select count(*) from users "
                                    f"where create_date > date_sub(NOW(), interval {from_days} day) and "
                                    f"users.city_id in "
                                    "(select city_id from all_cities where city_area = m)) as k, "
                                    "(select IFNULL(sum(payment_amount), 0) from payments "
                                    f"where payment_date > date_sub(NOW(), interval {from_days} day) and "
                                    "payment_status = 'succeeded' and user_id in "
                                    "(select user_id from users where users.city_id in "
                                    "(select city_id from all_cities where city_area = m))) "
                                    "from all_cities group by city_area "
                                    "order by k desc")
            count_users = session.query(Users).count()
            category_name = f'Области и края.\n\n' \
                            f'Всего пользователей: {count_users}'
        else:
            # area_name = session.query(Cities.city_area).filter(Cities.city_id == city_area)
            # print(area_name)
            items = session.execute("select city_id, city_name, (select count(*) from users "
                                    "where users.city_id = all_cities.city_id) as k, "
                                    "(select sum(payment_amount) from payments "
                                    "where payment_status = 'succeeded' and user_id in "
                                    "(select user_id from users where users.city_id = all_cities.city_id)) "
                                    "from all_cities "
                                    f"where city_area in (select city_area from all_cities "
                                    f"where city_id = {city_area}) "
                                    "order by k desc")
            count_users = session.execute(f'select count(*) from users where city_id in '
                                          f'(select city_id from all_cities where city_area =  '
                                          f'(select city_area from all_cities where city_id = {city_area}))').scalar_one()
            area_name = session.execute(f'select city_area from all_cities where city_id = {city_area}').scalar_one()
            category_name = f'{area_name}.\n\n' \
                            f'Всего пользователей: {count_users}'
        items: CursorResult
        new_items = []
        for row in items:
            new_items.append(row._asdict())
        items = new_items
    elif cat == 'categories':
        if parent_id:
            items = session.execute("select category_id, category_name "
                                    "from categories as m "
                                    f"where parent_id = {parent_id}")
            area_name = session.execute(f'select category_name '
                                        f'from categories where category_id = {parent_id}').scalar_one()
            category_name = f'Категории раздела {area_name}'
        elif from_category:
            items = session.execute("select brand_id, brand_name "
                                    "from brands as m "
                                    f"where category_id = {from_category} and parent_id is NULL")
            category_name = session.execute(f'select category_name '
                                            f'from categories where category_id = {from_category}').scalar_one()

            category_name = f'Категория {category_name}. Бренды'
            back_id = session.execute(f'select parent_id '
                                      f'from categories where category_id = {from_category}').scalar_one()
        elif set_category_id:
            closes_setting = int(closes_setting)
            if closes_setting == 0:
                items = session.execute("select brand_id, brand_name, '-', '--' "
                                        "from brands as m "
                                        f"where category_id = {set_category_id} and "
                                        f"parent_id = {request.args.get('part_brand_id')} and clothes_type is not NULL")
                category_name = session.execute(f'select category_name '
                                                f'from categories where category_id = {set_category_id}').scalar_one()
                key_name = 'brand_id'

            if closes_setting == 1:
                items = session.execute("select option_id, option_name, '-', '--' "
                                        "from options as m "
                                        f"where param_id = 14")
                category_name = session.execute(f'select category_name '
                                                f'from categories where category_id = {set_category_id}').scalar_one()
                key_name = 'option_id'
            if closes_setting == 2:
                items = session.execute("select option_id, option_name, '-', '--' "
                                        "from options as m "
                                        f"where param_id = 15")
                category_name = session.execute(f'select category_name '
                                                f'from categories where category_id = {set_category_id}').scalar_one()

                key_name = 'option_id'
            if closes_setting == 3:
                items = session.execute("select type_id, type_name, body_part, "
                                        "IFNULL((select type_name from closes_types "
                                        "where m.type_id = m.parent_id), '-') "
                                        "from closes_types as m "
                                        f"where is_type = 0 and category_id = {set_category_id}")
                category_name = session.execute(f'select category_name '
                                                f'from categories '
                                                f'where category_id = {set_category_id}').scalar_one()

                key_name = 'type_id'
            if closes_setting == 4:
                items = session.execute("select type_id, type_name, body_part, '-' "
                                        "from closes_types as m "
                                        f"where is_type = 1 and category_id = {set_category_id}")
                category_name = session.execute(f'select category_name '
                                                f'from categories '
                                                f'where category_id = {set_category_id}').scalar_one()

                key_name = 'type_id'
            brand_name = ''
            category_name = f'Категория {category_name}'
            back_id = session.execute(f'select parent_id '
                                      f'from categories where category_id = {set_category_id}').scalar_one()
        elif brand_id:
            back_id = session.execute(f'select category_id '
                                      f'from brands where brand_id = {brand_id}').scalar_one()
            if back_id not in (20, 21):
                count_serials = session.execute(f"select count(*) from brands "
                                                f"where parent_id = {brand_id} and is_serial = 1").scalar_one()
                if count_serials:
                    items = session.execute("select brand_id, brand_name "
                                            "from brands as m "
                                            f"where parent_id = {brand_id} and is_serial = 1")
                    brand_name = session.execute(f'select brand_name '
                                                 f'from brands where brand_id = {brand_id}').scalar_one()
                    brand_name = f'Бренд {brand_name}'
                else:
                    serial_id = brand_id
                    brand_id = 0
                    items = session.execute("select brand_id, brand_name "
                                            "from brands as m "
                                            f"where parent_id = {serial_id}")
                    brand_name = session.execute(f'select brand_name '
                                                 f'from brands where brand_id = {serial_id}').scalar_one()
                    brand_name = f'Серия {brand_name}'
                    count_serials = session.execute(f"select count(*) from brands "
                                                    f"where brand_id = {serial_id} and "
                                                    f"is_model = 0 and is_serial = 0").scalar_one()
            else:
                count_serials = session.execute(f"select count(*) from brands "
                                                f"where parent_id = {brand_id}").scalar_one()
                items = [
                    {
                        "brand_id": 0,
                        "name": "Бренды"
                    },
                    {
                        "brand_id": 1,
                        "name": "Размеры цифрами"
                    },
                    {
                        "brand_id": 2,
                        "name": "Размеры буквами"
                    },
                    {
                        "brand_id": 3,
                        "name": "Типы одежды"
                    },
                    {
                        "brand_id": 4,
                        "name": "Виды одежды"
                    }
                ]
                is_clothes = 1
                brand_name = session.execute(f'select brand_name '
                                             f'from brands where brand_id = {brand_id}').scalar_one()
        elif serial_id:
            count_serials = session.execute(f"select count(*) from brands "
                                            f"where brand_id = {serial_id} and "
                                            f"is_model = 0 and is_serial = 0").scalar_one()
            items = session.execute("select brand_id, brand_name "
                                    "from brands as m "
                                    f"where parent_id = {serial_id} and is_model = 1")
            brand_name = session.execute(f'select brand_name '
                                         f'from brands where brand_id = {serial_id}').scalar_one()
            brand_name = f'Серия {brand_name}'
            if not count_serials:
                back_id = session.execute(f'select parent_id '
                                          f'from brands where brand_id = {serial_id}').scalar_one()
            else:
                back_id = session.execute(f'select category_id '
                                          f'from brands where brand_id = {serial_id}').scalar_one()
        elif model_id:
            count_serials = session.execute(f"select count(*) from brands "
                                            f"where parent_id = {model_id} and is_model = 1").scalar_one()
            items = session.execute("select brand_param_id, "
                                    "(select param_name from params where params.param_id = m.param_id) as param_name, "
                                    "(select option_name from options where options.option_id = m.option_id) "
                                    "from brand_params as m "
                                    f"where brand_id = {model_id} and param_id not in (3, 4, 6) "
                                    f"order by param_position")
            brand_name = session.execute(f'select brand_name '
                                         f'from brands where brand_id = {model_id}').scalar_one()
            brand_name = f'Модель {brand_name}'
            back_id = session.execute(f'select parent_id '
                                      f'from brands where brand_id = {model_id}').scalar_one()
        elif option_id:
            items = session.execute("select option_id, "
                                    "(select param_name from category_params "
                                    "where category_params.param_id = m.param_id), "
                                    "option_name "
                                    "from options as m")
            area_name = session.execute(f'select option_name '
                                        f'from options where option_id = {option_id}').scalar_one()
            category_name = f'{area_name}. Список параметров'
            back_id = session.execute(f'select param_id '
                                      f'from options where option_id = {option_id} limit 1').scalar_one()
        else:
            items = session.execute("select category_id, category_name, tariff_first_price, "
                                    "tariff_second_price, tariff_notify_first, tariff_notify_second "
                                    "from categories as m "
                                    "where parent_id is NULL")
            category_name = f'Разделы'
        items: CursorResult
        new_items = []
        for row in items:
            if type(row) is not dict:
                new_items.append(row._asdict())
            else:
                new_items.append(row)
        items = new_items
        # if from_category:
        #     items = [items[0], items[-2], items[-3]]
    elif cat == 'utm':
        items = session.execute("select utm_id, date_create, bonus, "
                                "concat("
                                "(select count(*) from users where users.utm_id = utm.utm_id and is_get_bonus = 1), "
                                "'/', "
                                "(select count(*) from users where users.utm_id = utm.utm_id)"
                                "), "
                                "CONCAT('https://t.me/Jarvisrus_bot?start=', "
                                "TO_BASE64(CONCAT('utm_', utm_id)))"
                                "from utm order by utm_id desc")
        items: CursorResult
        new_items = []
        for row in items:
            new_items.append(row._asdict())
        items = new_items
    elif cat == 'payments':
        items = session.execute("select payment_id, user_id, date_format(payment_date, '%d-%m-%y %H:%i'), "
                                "IF(payment_status = 'succeeded', 'Успешно', 'В ожидании'), payment_amount, "
                                "system_id, (select city_name from all_cities where city_id = "
                                "(select city_id from users where user_id = payments.user_id)) "
                                "from payments "
                                "order by payment_date desc limit 500")
        items: CursorResult
        new_items = []
        for row in items:
            new_items.append(row._asdict())
        items = new_items
    elif cat == 'users':
        items = session.execute("select user_id, date_format(create_date, '%d-%m-%Y %H:%i'), tg_first_name, "
                                "tg_last_name, IF(tg_username is not NULL, tg_username, 'отсутствует'), is_live, "
                                "is_block, balance, (select count(*) from ads where ads.user_id = users.user_id and is_paid = 1), "
                                "(select sum(payment_amount) from payments where payments.user_id = users.user_id), "
                                "(select city_name from all_cities where city_id = "
                                "users.city_id) "
                                "from users "
                                "order by create_date desc")
        items: CursorResult
        new_items = []
        for row in items:
            new_items.append(row._asdict())
        items = new_items
    elif cat == 'ads':
        items = session.execute("select ad_id, "
                                "(select category_name from categories where category_id = ads.category_id), "
                                "(select category_name from categories where category_id = ads.section_id), "
                                "IF(ad_description, ad_description, 'описания нет'), user_id, ad_price, "
                                "tariff_price, DATE_FORMAT(date_close, '%d.%m.%Y %H:%i'), IF(is_warning, '⚠', 'нет') "
                                "from ads "
                                f"where is_warning = {is_warning} and is_paid = 1 and date_close > NOW() "
                                "order by date_create desc")
        items: CursorResult
        new_items = []
        for row in items:
            new_items.append(row._asdict())
        items = new_items
    else:
        items = session.query(cats[cat][0]).all()
        items = [item.as_dict() for item in items]

    if type(items) != list:
        d, a = {}, []
        for rowproxy in items:
            for column, value in rowproxy.items():
                d = {**d, **{column: value}}
            a.append(d)
        items = a

    session.close()
    if cat == 'categories':
        if parent_id:
            return render_template('categories.html',
                                   title="Категории и разделы", table_title=cat,
                                   items=items,
                                   id_name=cats[cat][1],
                                   category_name=category_name,
                                   head_names=cats[cat][4])
        elif from_category:
            return render_template('param_categories.html',
                                   title="Бренды", table_title=cat,
                                   items=items,
                                   id_name=cats['category_params'][1],
                                   category_name=category_name,
                                   head_names=cats['category_params'][4],
                                   back_id=back_id,
                                   back_name='parent_id',
                                   next_name='brand_id',
                                   key_name='brand_name')
        elif is_clothes:
            return render_template('clothes_settings.html',
                                   title="Серии", table_title=cat,
                                   items=items,
                                   id_name=cats['category_params'][1],
                                   category_name=brand_name,
                                   head_names=cats['category_params'][4],
                                   back_id=back_id,
                                   back_name='from_category',
                                   next_name='closes_setting',
                                   category_id=back_id,
                                   brand_id=brand_id,
                                   key_name='name',
                                   is_edit=1)
        elif brand_id:
            return render_template('param_categories.html',
                                   title="Серии", table_title=cat,
                                   items=items,
                                   id_name=cats['category_params'][1],
                                   category_name=brand_name,
                                   head_names=cats['category_params'][4],
                                   back_id=back_id,
                                   back_name='from_category',
                                   next_name='serial_id',
                                   key_name='brand_name',
                                   is_edit=1)
        elif set_category_id:
            return render_template('param_categories.html',
                                   title="Серии", table_title=cat,
                                   items=items,
                                   id_name=key_name,
                                   category_name=brand_name,
                                   head_names=cats['closes_types'][4],
                                   back_id=back_id,
                                   back_name='from_category',
                                   next_name='serial_id',
                                   key_name=key_name,
                                   is_add=1,
                                   add_table='brands',
                                   is_edit=1)
        elif serial_id:
            return render_template('param_categories.html',
                                   title="Модели", table_title=cat,
                                   items=items,
                                   id_name=cats['category_params'][1],
                                   category_name=brand_name,
                                   head_names=cats['category_params'][4],
                                   back_id=back_id,
                                   back_name='brand_id' if not count_serials else 'from_category',
                                   next_name='model_id',
                                   key_name='brand_name')
        elif model_id:
            return render_template('param_categories.html',
                                   title="Параметры модели", table_title=cat,
                                   items=items,
                                   category_name=brand_name,
                                   id_name='brand_param_id',
                                   head_names=cats['param_brand_options'][4],
                                   back_id=back_id,
                                   back_name='model_id' if count_serials else 'serial_id',
                                   next_name='brand_param_id',
                                   key_name='param_name',
                                   is_edit=1,
                                   is_add=1,
                                   edit_table='brand_params',
                                   delete_table='brand_params',
                                   add_table='params')
        elif option_id:
            return render_template('option_brand_params.html',
                                   title="Категории и разделы", table_title=cat,
                                   items=items,
                                   id_name=cats['param_brand_options'][1],
                                   category_name=category_name,
                                   option_id=option_id,
                                   head_names=cats['param_brand_options'][4],
                                   back_id=back_id)
        elif param_id:
            return render_template('param_options.html',
                                   title="Категории и разделы", table_title=cat,
                                   items=items,
                                   id_name=cats['param_options'][1],
                                   category_name=category_name,
                                   head_names=cats['param_options'][4],
                                   back_id=back_id)
        else:
            return render_template('head_categories.html',
                                   title="Категории и разделы", table_title=cat,
                                   items=items,
                                   id_name=cats['head_categories'][1],
                                   category_name=category_name,
                                   head_names=cats['head_categories'][4])
    elif cat == 'all_cities':
        return render_template('stats.html' if not city_area else 'stats_by_city.html',
                               title="Статистика по городам", table_title=cat,
                               items=items,
                               id_name=cats[cat][1],
                               category_name=category_name,
                               head_names=cats[cat][4])
    elif cat == 'ads':
        return render_template('ads.html',
                               title="Объявления пользователей", table_title=cat,
                               items=items,
                               id_name=cats[cat][1],
                               category_name=category_name,
                               is_warning=int(is_warning),
                               head_names=cats[cat][4])
    elif cat == 'lists':
        if param_id:
            return render_template('lists_options.html',
                                   title="Список опций", table_title=cat,
                                   items=items,
                                   id_name=cats['options'][1],
                                   category_name=category_name,
                                   param_id=param_id,
                                   head_names=cats['options'][4])
        else:
            return render_template('lists.html',
                                   title="Списки параметров", table_title=cat,
                                   items=items,
                                   id_name=cats[cat][1],
                                   category_name=category_name,
                                   head_names=cats[cat][4])
    elif cat == 'withdrawal':
        return render_template('withdrawal.html',title='Выводы', table_title=cat,
                               items=items,
                               category_name=category_name,
                               id_name=cats[cat][1],
                               head_names=cats[cat][2]
                               )
    else:
        return render_template('index.html', title="Главная", table_title=cat,
                               items=items,
                               id_name=cats[cat][1],
                               category_name=category_name,
                               head_names=cats[cat][4],
                               is_add=1 if cat not in ('users', 'payments') else 0)


@app.route("/add/<cat>", methods=["GET", "POST"])
@auth.login_required
def add_item(cat):
    option_id = request.args.get('option_id')
    param_id = request.args.get('param_id')
    forms = generate_forms(option_id=option_id, param_id=param_id)
    if cat not in forms.keys():
        abort(404)
    session = db_session.create_session()
    if cat == 'lists' and param_id:
        execute_cat = 'options'
    else:
        execute_cat = cat
    form = forms[execute_cat]()

    if form.validate_on_submit():
        data = form.data

        for k, v in data.items():
            if 'photos' in k:

                if v:
                    new_v = []
                    for q in v:

                        new_v.append(photo_upload(q))
                    data[k] = new_v
                else:
                    data[k] = []
            elif 'photo' in k:

                if v:
                    data[k] = photo_upload(v)
                else:
                    data[k] = ''
        if 'mail_photo' in data.keys():
            data: dict
            if data['mail_photo']:
                data['mail_additional_ident'] = data['mail_photo']
            del data['mail_photo']
        del data['csrf_token']
        item = cats[execute_cat][0](**data)
        session.add(item)
        session.commit()
        session.close()
        url = url_for("index", cat=cat)
        if param_id:
            url = f'{url}&param_id={param_id}'
        return redirect(url)
    session.close()
    return render_template('form.html', title=f'Редактирование {cats[cat][3]}', form=form,
                           form_title=f"Добавление {cats[cat][3]}")


@app.route("/<cat>/<int:id>", methods=["GET", "POST"])
@auth.login_required
def edit_item(cat, id):
    forms = generate_forms(brand_param_id=id if cat == 'brand_params' else None)
    if cat not in forms.keys():
        abort(404)
    form = forms[cat]()
    session = db_session.create_session()
    if request.method == "GET":
        item = session.query(cats[cat][0]).get(id)
        if item:
            form = forms[cat](data=item.as_dict())
        else:
            session.close()
            abort(404)
    elif form.validate_on_submit():
        item = session.query(cats[cat][0]).get(id)
        if item:

            data = form.data
            del data['csrf_token']
            for k, v in data.items():
                if 'photos' in k:

                    if v:
                        new_v = []
                        brand_id = session.execute(
                            f"select brand_id from brand_params where brand_param_id = {id}").scalar()
                        for q in v:
                            photo_link = photo_upload(q)

                            session.execute(f"insert into brands_photos (brand_id, color_id, photo_link) "
                                            f"values ({brand_id}, {id}, '{str(photo_link)}')")
                            session.commit()
                            new_v.append(photo_link)
                        data[k] = new_v
                    else:
                        data[k] = []
                elif 'photo' in k:
                    if v:
                        v = photo_upload(v)
                    else:
                        v = ''
                item.__setattr__(k, v)
            if cat == 'brand_params':
                brand_id = session.execute(f"select brand_id from brand_params where brand_param_id = {id}").scalar()
                url = url_for("index", cat='categories', model_id=brand_id)
            else:
                url = url_for("index", cat=cat)
            session.commit()
            session.close()
            return redirect(url)
        else:
            session.close()
            abort(404)

    if cat == 'ads':
        photos = session.execute(f"select photo_id, photo_link "
                                 f"from ads_photos where ad_id = {id}")
        new_items = []
        for row in photos:
            new_items.append(row._asdict())
        photos = new_items

        session.close()
        return render_template('ad_form.html', title=f'Редактирование {cats[cat][3]} № {id}', form=form,
                               form_title=f'Редактирование {cats[cat][3]} № {id}',
                               photos=photos)
    elif cat == 'brand_params':
        photos = session.execute(f"select bp_id, photo_link "
                                 f"from brands_photos where color_id = {id}")
        new_items = []
        for row in photos:
            new_items.append(row._asdict())
        photos = new_items

        session.close()
        return render_template('edit_ad_options.html', title=f'Редактирование {cats[cat][3]} № {id}', form=form,
                               form_title=f'Редактирование {cats[cat][3]} № {id}',
                               photos=photos)
    else:
        session.close()
        return render_template('form.html', title=f'Редактирование {cats[cat][3]} № {id}', form=form,
                               form_title=f'Редактирование {cats[cat][3]} № {id}')


@app.route('/delete/<cat>/<int:id>', methods=['GET', 'POST'])
@auth.login_required
def delete_item(cat, id):
    if cat == 'ads_photos':
        session = db_session.create_session()
        item = session.query(cats[cat][0]).get(id)

        if item:
            session.delete(item)
            session.commit()
            session.close()
        else:
            session.close()
            return abort(404)
        return redirect(f'/ads/{item.ad_id}')
    elif cat == 'brands_photos':
        session = db_session.create_session()
        item = session.query(cats[cat][0]).get(id)

        if item:
            session.delete(item)
            session.commit()
            session.close()
        else:
            session.close()
            return abort(404)
        return redirect(f'/brand_params/{item.brand_id}')
    elif cat == 'ads':
        redirect_cat = cat
        if cat == 'options':
            redirect_cat = 'lists'
        if cat not in cats.keys():
            abort(404)
        session = db_session.create_session()
        user_id = session.execute(f"select user_id from ads where ad_id = {id}").scalar()

        session.execute(f"update users set balance = balance + (select tariff_price from ads where ad_id = {id}) "
                        f"where user_id = {user_id}")
        session.commit()
        try:
            async def send_message():
                await bot.send_message(user_id,
                                       f'⚠ <b>Ваше объявление удалено так как оно нарушает правила. '
                                       f'Деньги возвращены</b>')

            asyncio.run(send_message())
        except Exception as e:
            logging.info(e, exc_info=True)
        item = session.query(cats[cat][0]).get(id)
        if item:
            session.delete(item)
            session.commit()
            session.close()
        else:
            session.close()
            return abort(404)
        return redirect(url_for('index', cat=redirect_cat))
    else:
        redirect_cat = cat
        if cat == 'options':
            redirect_cat = 'lists'
        if cat not in cats.keys():
            abort(404)
        session = db_session.create_session()
        item = session.query(cats[cat][0]).get(id)
        if item:
            session.delete(item)
            session.commit()
            session.close()
        else:
            session.close()
            return abort(404)
        return redirect(url_for('index', cat=redirect_cat))


@app.errorhandler(404)
@auth.login_required
def not_found(error):
    return render_template('404.html')


def photo_upload(data):
    return 'https://telegra.ph{}'.format(requests.post('https://telegra.ph/upload',
                                                       files={
                                                           'file': ('file', data, 'image/jpeg')
                                                       }).json()[0]['src'])


if __name__ == "__main__":
    db_session.global_init("mysql+pymysql://{}:{}@{}:{}/{}".format(
        os.getenv('DBUSER', 'root'), os.getenv('DBPASS', config.DB_PASSWORD), os.getenv('DBHOST', 'localhost'),
        os.getenv('DBPORT', 3306), os.getenv('DBNAME', config.DB_NAME)
    ))
    app.run(host='0.0.0.0', port=8080)
