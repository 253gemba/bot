import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

from filters.filters import IsManager
from handlers.users.state_get_referral import process_message
from keyboards.default import default_keyboards, default_buttons
from keyboards.inline import dynamic_keyboards
from keyboards.inline.dynamic_keyboards import withdrawal
from loader import dp, bot
from states.states import GetReferral
from utils.ads import ad_info, find_info
from utils.referral import referrals
from utils.partnership import partnership
from utils.ads.ad_info import show_ads
from utils.db_api.python_mysql import mysql_connection
from utils.find.make_find import find_results


@dp.message_handler(IsManager(),
                    lambda message: message.text in default_keyboards.get_buttons_text_from_menu(
                        default_keyboards.my_profile_menu),
                    content_types="any", state="*")
async def user_menu_header(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    msg_text = str(message.text)
    conn = mysql_connection()
    c = conn.cursor(buffered=True)
    logging.info(f'{user_id} {msg_text}')
    state_data = await state.get_data()
    state_state = await state.get_state()
    await state.finish()

    if msg_text == default_buttons.button_referral.text:
        if partnership.is_exist(user_id):
            c.execute('select bonus_balance, referral, referred from referrals where user = %s', (user_id, ))
            try:
                balance, link, referred = c.fetchone()
            except TypeError:
                referrals.create_referral(user_id, c, conn)
            c.execute('select bonus_balance, referral, referred, attached_referrals '
                      'from referrals where user = %s', (user_id,))
            balance, link, referred, attached = c.fetchone()
            withdraw_balance = 0
            if balance > 250:
                withdraw_balance = balance
            await message.answer(f"🤝 <b>Партнерская программа</b>\n\n"
                                 f"🥇 <b>Статистика</b>:\n"
                                 f"├  <b>Всего заработано:</b> {balance}₽\n"
                                 f"├  <b>Доступно к выводу:</b> {withdraw_balance}₽\n"
                                 f"└  <b>Лично приглашенных:</b> {referred}\n"
                                 f"<b>⤵️ Ваша ссылка⤵️</b> \n"
                                 f'https://t.me/Jarvisrus_bot?start={link}', reply_markup=withdrawal())
        else:
            await message.answer('К сожалению, у вас нет доступа к партнерской программе 😢')

    elif msg_text == default_buttons.button_my_balance.text:
        c.execute("select balance from users where user_id = %s", (user_id,))
        balance = c.fetchone()[0]
        await bot.send_message(user_id,
                               f'💰 <b>Ваш баланс:</b> {balance} ₽',
                               reply_markup=dynamic_keyboards.balance_menu())
    elif msg_text == default_buttons.button_change_city.text:
        # c.execute("update users set city_id = NULL where user_id = %s", (user_id,))
        # conn.commit()
        await message.answer("🗺 Как будем определять регион поиска/размещения объявлений?",
                             reply_markup=default_keyboards.select_geo(is_edit=1))
    elif msg_text == default_buttons.button_my_ads.text:
        result_text, inline_kb = await show_ads(c, page=1, user_id=user_id, is_my_ads=1)
        await message.answer(result_text,
                             reply_markup=inline_kb)
    elif msg_text == default_buttons.button_favourites.text:
        c.execute("select ad_id from favourites_ads "
                  "where user_id = %s and "
                  "(select count(*) from ads where ads.ad_id = favourites_ads.ad_id)",
                  (user_id,))
        all_ads = [x[0] for x in c.fetchall()]
        if not all_ads:
            await message.answer("😴 Здесь пока что пусто. Здесь появятся объявления после того, как Вы "
                                 "добавите в избранное хотя бы одно объявление")
        else:
            inline_kb = await dynamic_keyboards.get_ad_menu(c, all_ads[0], user_id, find_id=0,
                                                            count_pages=len(all_ads), page=0, is_favourites=1)
            ad_text = await ad_info.get_ad_text(c, all_ads[0], user_id)
            await message.answer(text=f'{ad_text}',
                                 reply_markup=inline_kb)
    elif msg_text == default_buttons.button_notifications.text:
        c.execute("select find_id from finds where user_id = %s and is_notify = 1 and is_paid = 1", (user_id,))
        all_finds = c.fetchall()
        for one_find in all_finds:
            find_id = one_find[0]
            all_ads = await find_results(c, find_id)
            await message.answer(f"{await find_info.get_find_text(c, find_id, count_ads=len(all_ads))}",
                                 reply_markup=await dynamic_keyboards.get_notify_menu(c, find_id))
        if not all_finds:
            await message.answer("😴 Уведомления пока не добавлены. Добавьте первое оповещение о новых объявлениях "
                                 "при помощи команды /notifications")
    c.close()
    conn.close()
