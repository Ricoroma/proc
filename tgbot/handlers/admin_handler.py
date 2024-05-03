from random import randint

from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.utils.formatting import Text
from aiogram.filters import Command
from sqlalchemy.orm import Session

from tgbot.data import loader
from tgbot.data.loader import bot, links
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext

from tgbot.keyboards.admin_keyboards import *
from tgbot.services.database import User, Trader, Trade, Settings
from tgbot.filters.is_adm import IsAdmin
from tgbot.utils.curs import get_course
from tgbot.utils.other import format_trades
from tgbot.utils.states import TraderState, AdminState

router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

statuses = {}


@router.callback_query(F.data == "main_admin")
@router.message(Command("start"))
async def admin_start_handler(update: Message | CallbackQuery):
    if isinstance(update, CallbackQuery):
        await update.message.delete()
        func = update.message.answer
    else:
        func = update.answer
    await func('Главное меню', reply_markup=main_admin_kb())


@router.callback_query(F.data == 'admin_traders')
@router.message(F.text == 'Трейдеры 👤')
async def admin_traders_handler(update: Message | CallbackQuery, db_session: Session):
    traders = [i.user_id for i in db_session.query(Trader).all()]
    if isinstance(update, CallbackQuery):
        func = update.message.edit_text
    else:
        func = update.answer

    text = 'Выберите трейдера:'

    await func(text, reply_markup=choose_trader_kb(traders))


@router.callback_query(F.data.startswith('trader:'))
async def admin_trader_handler(call: CallbackQuery, db_session: Session, state: FSMContext):
    trader_id = int(call.data.split(':')[1])
    trader: Trader = db_session.query(Trader).get(trader_id)
    text = f'Трейдер {trader_id}\n' \
           f'Баланс: {trader.balance} BTC\n' \
           f'Кошелек: {trader.wallet or "Некоторый кошелек"}\n' \
           f'Привязанный аккаунт: {trader.account_id or "Не привязан"}\n'

    await call.message.edit_text(text, reply_markup=admin_trader_menu(trader.is_active))
    await state.update_data(trader_id=trader_id)


@router.callback_query(F.data == 'admin_trader_status')
async def admin_trader_status_handler(call: CallbackQuery, state: FSMContext, db_session: Session):
    data = await state.get_data()
    trader_id = data.get('trader_id')
    trader: Trader = db_session.query(Trader).get(trader_id)

    await call.message.edit_text('Выберите статус:', reply_markup=admin_trader_status_kb(trader.is_active, trader_id))


@router.callback_query(F.data.startswith('trader_status:'))
async def admin_trader_status_change_handler(call: CallbackQuery, state: FSMContext, db_session: Session):
    status = int(call.data.split(':')[1])
    data = await state.get_data()
    trader_id = data.get('trader_id')

    trader: Trader = db_session.query(Trader).get(trader_id)
    trader.is_active = status
    db_session.commit()

    await call.message.edit_text('Статус изменен', reply_markup=admin_management_kb(status, trader_id))
    await bot.send_message(trader_id, f'Администратор {"включил" if status else "выключил"} вам торговлю')


@router.callback_query(F.data == 'admin_trader_requisites')
async def admin_trader_requisites_handler(call: CallbackQuery, state: FSMContext, db_session: Session):
    data = await state.get_data()
    trader_id = data.get('trader_id')

    trader = db_session.query(Trader).get(trader_id)
    requisites = trader.requisites.split('|')

    await call.message.edit_text('Выберите реквизит для удаления:',
                                 reply_markup=admin_requisites_kb(requisites, trader_id))


@router.callback_query(F.data.startswith('del_requisite:'))
async def admin_trader_requisites_del_handler(call: CallbackQuery, db_session: Session, state: FSMContext):
    requisite = call.data.split(':')[1]
    data = await state.get_data()
    trader_id = data.get('trader_id')

    trader = db_session.query(Trader).get(trader_id)
    requisites = trader.requisites.split('|')
    requisites.remove(requisite)
    trader.requisites = '|'.join(requisites)
    db_session.commit()

    await call.message.edit_text('Реквизит удален', reply_markup=admin_requisites_kb(requisites, trader_id))


@router.callback_query(F.data == 'admin_trader_management')
async def admin_trader_management_handler(call: CallbackQuery, state: FSMContext, db_session: Session):
    data = await state.get_data()
    trader_id = data.get('trader_id')

    trader = db_session.query(Trader).get(trader_id)

    await call.message.edit_text('Управление', reply_markup=admin_management_kb(trader.is_active, trader_id))


@router.callback_query(F.data == 'trader_change_balance')
async def admin_trader_change_balance_handler(call: CallbackQuery, state: FSMContext):
    await call.message.answer('Введите новый баланс трейдера', reply_markup=cancel_change_kb())
    await state.set_state(AdminState.change_balance)
    await call.answer()


@router.message(AdminState.change_balance)
async def admin_trader_change_balance_handler(message: Message, state: FSMContext, db_session: Session):
    data = await state.get_data()
    trader_id = int(data.get('trader_id'))

    if message.text.replace(',', '', 1).replace('.', '', 1).isdigit():
        trader = db_session.query(Trader).get(trader_id)
        old_balance = trader.balance
        trader.balance = float(message.text)
        db_session.commit()

        await message.answer('Баланс изменен ✅')

        text = f'Трейдер {trader_id}\n' \
               f'Баланс: {trader.balance} BTC\n' \
               f'Кошелек: {trader.wallet or "Некоторый кошелек"}\n' \
               f'Привязанный аккаунт: {trader.account_id or "Не привязан"}\n'

        await message.answer(text, reply_markup=admin_trader_menu(trader.is_active))

        await bot.send_message(trader_id, f'Администратор изменил ваш баланс с {old_balance} на {trader.balance} BTC')

        await state.set_state(None)
    else:
        await message.answer('Введите корректное десятичное число с разделителем "." или ","')


@router.callback_query(F.data == 'create_link')
async def create_link_handler(call: CallbackQuery, db_session: Session):
    if db_session.query(Trader).first():
        await call.answer('Достигнуто максимальное количество трейдеров')
        return

    code = randint(10 ** 7, 10 ** 8)
    links.append(code)
    traders = [i.user_id for i in db_session.query(Trader).all()]
    await call.message.edit_text(
        f'Ссылка для приглашения трейдера: https://t.me/{(await bot.me()).username}?start={code}',
        reply_markup=choose_trader_kb(traders)
    )


@router.message(F.text == 'Статистика 📈')
@router.callback_query(F.data == 'statistics')
async def statistics_handler(update: Message | CallbackQuery, db_session: Session):
    if isinstance(update, CallbackQuery):
        func = update.message.edit_text
    else:
        func = update.answer

    traders = [i.user_id for i in db_session.query(Trader).all()]
    trades = db_session.query(Trade).all()

    await func(format_trades(trades), reply_markup=statistics_kb(traders))


@router.callback_query(F.data.startswith('statistics:'))
async def trader_statistics_handler(call: CallbackQuery, db_session: Session):
    trader_id = int(call.data.split(':')[1])
    trades = db_session.query(Trade).filter(Trade.trader_id == trader_id).all()

    text = f'Статистика трейдера {trader_id}\n' + format_trades(trades)

    await call.message.edit_text(text, reply_markup=trader_statistics_kb())


@router.callback_query(F.data.startswith('refill_confirmed'))
async def refill_confirmed_handler(call: CallbackQuery, db_session: Session):
    trader_id, amount = call.data.split(':')[1:]
    trader_id = int(trader_id)
    amount = float(amount)

    trader: Trader = db_session.query(Trader).get(trader_id)
    trader.balance += amount
    db_session.commit()

    await call.message.edit_text(f'Пополнение трейдеру {trader_id} на {amount} BTC подтверждено')

    await bot.send_message(trader_id, f'Ваш баланс пополнен на {amount} BTC')


@router.callback_query(F.data == 'no_button')
async def no_button_handler(call: CallbackQuery):
    await call.answer('Для выключения торговли трейдеру перейдите в Управление', show_alert=True)


@router.message(F.text == 'Настройки ⚙️')
@router.callback_query(F.data == 'settings')
async def settings_handler(update: Message | CallbackQuery, state: FSMContext, db_session: Session):
    await state.set_state(None)

    if isinstance(update, CallbackQuery):
        func = update.message.edit_text
    else:
        func = update.answer

    settings = db_session.query(Settings).first()

    await func(f'Текущий API-ключ: {settings.api_key}\n'
               f'Текущий адрес пополнения:\n<code>{settings.refill_address}</code>', reply_markup=settings_kb())


@router.callback_query(F.data.startswith('change:'))
async def change_handler(call: CallbackQuery, state: FSMContext):
    await state.set_state(AdminState.settings_change)

    action = call.data.split(':')[1]
    await state.update_data(action=action)

    await call.message.answer('Введите новое значение', reply_markup=cancel_change_kb())
    await call.answer()


@router.message(AdminState.settings_change)
async def change_value_handler(message: Message, state: FSMContext, db_session: Session):
    data = await state.get_data()
    action = data.get('action')

    if action == 'api_key':
        db_session.query(Settings).update({Settings.api_key: message.text})
    elif action == 'refill_address':
        db_session.query(Settings).update({Settings.refill_address: message.text})

    db_session.commit()

    await message.answer('Значение изменено ✅')
    await settings_handler(message, state, db_session)


@router.callback_query(F.data == 'cancel_change')
async def cancel_change_handler(call: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    await call.answer('Изменение отменено ❌')
    await call.message.delete()


@router.callback_query(F.data == 'trader_delete')
async def delete_trader_handler(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    trader_id = int(data.get('trader_id'))

    await call.message.edit_text(f'Подтвердите удаление трейдера {trader_id}?', reply_markup=trader_delete_confirm_kb())


@router.callback_query(F.data == 'trader_delete_confirm')
async def trader_delete_confirm_handler(call: CallbackQuery, state: FSMContext, db_session: Session):
    data = await state.get_data()
    trader_id = int(data.get('trader_id'))

    db_session.query(Trader).filter(Trader.user_id == trader_id).delete()
    traders = [i.user_id for i in db_session.query(Trader).all()]
    await call.message.edit_text(
         f'Трейдер {trader_id} удален из списка трейдеров. Вы возвращены в меню выбора трейдера',
        reply_markup=choose_trader_kb(traders)
    )


@router.callback_query(F.data == 'add_account')
async def add_account_handler(call: CallbackQuery, state: FSMContext):
    await state.set_state(AdminState.add_account)
    await call.message.answer('Введите ID аккаунта', reply_markup=cancel_change_kb())
    await call.answer()


@router.message(AdminState.add_account)
async def add_account_handler(message: Message, state: FSMContext, db_session: Session):
    data = await state.get_data()
    trader_id = int(data.get('trader_id'))

    trader = db_session.query(Trader).get(trader_id)
    trader.account_id = message.text
    db_session.commit()

    await message.answer('Аккаунт привязан ✅')
    text = f'Трейдер {trader_id}\n' \
           f'Баланс: {trader.balance} BTC\n' \
           f'Кошелек: {trader.wallet or "Некоторый кошелек"}\n' \
           f'Привязанный аккаунт: {trader.account_id or "Не привязан"}\n'

    await message.answer(text, reply_markup=admin_trader_menu(trader.is_active))

    await state.set_state(None)
