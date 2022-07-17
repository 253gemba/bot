from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateTimeField, FileField, TextAreaField, SelectField, BooleanField, widgets
from wtforms.validators import DataRequired


class UtmForm(FlaskForm):
    bonus = StringField('Введите бонус в рублях', validators=[DataRequired()], default=0)


class UsersForm(FlaskForm):
    user_id = IntegerField('ID пользователя в телеграм', validators=[DataRequired()])
    balance = IntegerField('Баланс', validators=[DataRequired()])
    is_block = BooleanField('Блокировка')


class PaymentsForm(FlaskForm):
    user_id = IntegerField('ID пользователя в телеграм', validators=[DataRequired()])
    payment_status = SelectField('Статус платежа', validators=[DataRequired()],
                                 choices=['wait', 'succeeded'])
    payment_date = DateTimeField('Дата и время платежа', format='%d.%m.%Y %H:%M')
    payment_amount = IntegerField('Сумма пополнения', validators=[DataRequired()])
    system_id = StringField('ID платежа в платежной системе', validators=[DataRequired()])
