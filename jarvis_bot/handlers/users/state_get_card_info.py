from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp
from states.states import GetCreditCard
from utils.withdrawal.withdrawal import create_withdrawal, get_amount, insert_amount


@dp.message_handler(state=GetCreditCard.card)
async def process_message(message: types.Message, state: FSMContext):
    card_num = message.text
    current_user = message.from_id
    flag = True
    stripped_num = card_num.replace(' ', '')
    try:
        int(stripped_num)
    except ValueError:
        flag = False
    if flag is False:
        await message.answer('<b>Разрешены только числа</b>')
    else:
        if len(stripped_num) == 16:
            create_withdrawal(current_user, stripped_num)
        else:
            await message.answer('<b>Неверное количество символов</b>')
    await GetCreditCard.next()
    await message.answer('<b>Введите сумму для вывода:</b>')


@dp.message_handler(state=GetCreditCard.amount)
async def process_message_next(message: types.Message, state: FSMContext):
    amount = message.text
    current_user = message.from_id
    flag = True
    try:
        int_amount = int(amount)
    except ValueError:
        flag = False
    int_amount = int(amount)
    if flag is False:
        await message.answer('<b>Разрешены только числа</b>')
    else:
        available = get_amount(current_user)
        if int_amount > available:
            await message.answer(f'<b>На балансе недостаточно средств.\n'
                                 f'Вы запросили: {amount}\n'
                                 f'Доступно: {available}</b>')
        elif int_amount < 250:
            await message.answer('<b>Минимальная сумма вывода - 250 рублей</b>')
        else:
            insert_amount(current_user, int_amount)
            await message.answer('<b>Заявка на вывод создана!</b>')
        await state.finish()
