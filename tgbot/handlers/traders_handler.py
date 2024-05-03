import datetime
from typing import Type

from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.utils.formatting import Text
from aiogram.filters import Command
from sqlalchemy.orm import Session

from tgbot.data import loader, config
from tgbot.data.loader import bot
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext

from tgbot.keyboards.admin_keyboards import trader_refill_confirm
from tgbot.keyboards.traders_keyboards import _state
from tgbot.services.database import User, Trader, Settings, Trade, Requisite
from tgbot.filters.is_trader import IsTrader
from tgbot.keyboards.traders_keyboards import *
from tgbot.utils.curs import get_course
from tgbot.utils.other import format_trades, format_requisites
from tgbot.utils.states import TraderState

router = Router()
router.message.filter(IsTrader())
router.callback_query.filter(IsTrader())


@router.callback_query(F.data == "main_menu")
@router.message(Command("start"))
async def trader_start_handler(update: Message | CallbackQuery):
    if isinstance(update, CallbackQuery):
        await update.message.delete()
        func = update.message.answer
    else:
        func = update.answer

    await func('Главное меню', reply_markup=main_menu_kb())


# @router.callback_query(F.data == 'lk')
@router.message(F.text == 'Кошелек 💼')
async def trader_personal_cabinet_handler(update: Message | CallbackQuery, db_session: Session):
    if isinstance(update, CallbackQuery):
        func = update.message.edit_text
    else:
        func = update.answer

    trader = db_session.query(Trader).get(update.from_user.id)
    text = f'Ваш биткоин-кошелек:\n<code>некоторый кош</code>\n\n' \
           f'Ваш баланс:\n├{trader.balance}₿\n└ {round(get_course() * trader.balance, 2)}\n\n' \
           f'Эскроу:\n├ 0,00000000₿\n└ 0,00₽\n\n' \
           f'Курс биржи: {get_course()} RUB\n\n'

    await func(text)


# @router.callback_query(F.data == 'wallet')
# async def trader_wallet_handler(call: CallbackQuery, db_session: Session):
#     trader = db_session.query(Trader).get(call.from_user.id)
#     text = f'Ваш биткоин-кошелек:\n<code>некоторый кош</code>\n\n' \
#            f'Ваш баланс: {trader.balance} BTC ({get_course("BTC")} RUB)\n\n' \
#            f'В эскроу: 0 BTC (0 RUB)\n\n' \
#            f'Курс для меня: {get_course("BTC")} RUB\n\n'
#
#     await call.message.edit_text(text, reply_markup=back_lk_kb())

# @router.
#
# @router.callback_query(F.data == 'refill')
# async def trader_refill_handler(call: CallbackQuery, state: FSMContext):
#     await state.set_state(TraderState.refill)
#
#     await call.message.edit_text('Введите сумму для пополнения баланса:', reply_markup=back_lk_kb())


# @router.message(TraderState.refill)
# async def trader_refill_sum_handler(message: Message, state: FSMContext, db_session: Session):
#     if message.text.replace('.', '', 1).replace(',', '', 1).isdigit():
#         amount = float(message.text.replace(',', '.'))
#         settings = db_session.query(Settings).first()
#         address = settings.refill_address
#
#         await message.answer(f'Для пополнения баланса переведите <code>{amount}</code> BTC на адрес:\n'
#                              f'<code>{address}</code>\n', reply_markup=refill_kb())
#         await state.set_state(None)
#         await state.update_data(amount=amount)
#     else:
#         await message.answer('Введите корректную сумму', reply_markup=back_lk_kb())


# @router.callback_query(F.data == 'refill_confirm')
# async def trader_refill_confirm_handler(call: CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     amount = data.get('amount')
#
#     for admin in config.admin_ids:
#         await bot.send_message(
#             admin,
#             f'Трейдер {call.from_user.id} запросил пополнение на {amount} BTC',
#             reply_markup=trader_refill_confirm(call.from_user.id, amount)
#         )
#
#     await call.message.edit_text('Запрос на пополнение отправлен администраторам', reply_markup=back_lk_kb())


@router.callback_query(F.data == 'info')
async def trader_info_handler(call: CallbackQuery):
    await call.message.edit_text('Выберите действие:', reply_markup=info_kb())


@router.callback_query(F.data == 'trader_stats')
async def trader_stats_handler(call: CallbackQuery, db_session: Session):
    trades: list[Type[Trade]] = db_session.query(Trade).filter(Trade.trader_id == call.from_user.id).all()

    await call.message.edit_text(format_trades(trades), reply_markup=back_info_kb())


@router.callback_query(F.data == 'trader_deals')
async def trader_deals_handler(call: CallbackQuery, db_session: Session):
    trader = db_session.query(Trader).get(call.from_user.id)
    if not trader.trades:
        text = 'У вас нет сделок'
    else:
        text = 'Ваши сделки:\n\n'
        for deal in trader.trades:
            text += f'• {deal.amount} RUB {deal.date} {_state(deal.state)}\n'

    await call.message.edit_text(text, reply_markup=back_info_kb())


@router.callback_query(F.data == 'trader_report')
async def trader_report_handler(call: CallbackQuery):
    await call.message.edit_text('Отчет пуст', reply_markup=back_info_kb())


@router.callback_query(F.data == 'trader_history')
async def trader_history_handler(call: CallbackQuery):
    await call.message.edit_text('История депозитов', reply_markup=back_info_kb())


@router.callback_query(F.data == 'cards')
@router.message(F.text == 'Карты 💳')
async def trader_cards_handler(update: Message | CallbackQuery, state: FSMContext):
    await state.set_state(None)

    if isinstance(update, CallbackQuery):
        func = update.message.edit_text
    else:
        func = update.answer

    await func('Выберите действие:', reply_markup=cards_kb())


@router.callback_query(F.data == 'add_card')
async def start_add_cart_handler(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text('Выбор эмитента реквизита:', reply_markup=choose_bank())

    await state.set_state(TraderState.new_card)


@router.callback_query(F.data.startswith('bank:'))
async def choose_bank_handler(call: CallbackQuery, state: FSMContext):
    bank = call.data.split(':')[1]
    if bank == 'all':
        await call.answer('Пока пусто')
        return
    elif bank == 'tin':
        bank = 'Тинькофф'
    elif bank == 'sber':
        bank = 'Сбербанк'

    await state.update_data(bank=bank)
    await state.set_state(TraderState.new_card)
    await call.message.edit_text(f'Эмитент: {bank}\nВведите номера карт через пробел:')


@router.message(TraderState.new_card)
async def add_new_card_handler(message: Message, state: FSMContext, db_session: Session):
    await state.set_state(None)
    data = await state.get_data()

    reqs = [Requisite(bank=data['bank'], value=i, user_id=message.from_user.id) for i in message.text.split(' ')]
    db_session.add_all(reqs)

    db_session.commit()
    reqs = db_session.query(Requisite).filter(Requisite.user_id == message.from_user.id).all()

    await message.answer(f'Эмитент: {data["bank"]}\nДобавленные реквизиты:\n{format_requisites(reqs)}')
    await message.answer('Выберите действие:', reply_markup=cards_kb())


@router.callback_query(F.data == 'delete_card')
async def start_delete_card_handler(call: CallbackQuery, db_session: Session):
    trader: Trader = db_session.query(Trader).get(call.from_user.id)
    reqs = trader.requisites

    await call.message.edit_text('Выберите карту для удаления', reply_markup=delete_cards_kb(reqs))


@router.callback_query(F.data.startswith('del_card:'))
async def delete_card_handler(call: CallbackQuery, db_session: Session):
    req_id = call.data.split(':')[1]

    req: Type[Requisite] = db_session.query(Requisite).filter(Requisite.id == int(req_id)).first()

    await call.message.edit_text(f'{req.value} - {req.bank} удален')
    await call.message.answer('Выберите действие:', reply_markup=cards_kb())

    db_session.delete(req)
    db_session.commit()


@router.callback_query(F.data == 'delete_all_cards')
async def delete_all_cards_handler(call: CallbackQuery, db_session: Session):
    trader = db_session.query(Trader).get(call.from_user.id)
    reqs = trader.requisites

    await call.message.edit_text(f'Реквизиты:\n\n{format_requisites(reqs)}\n\nУдалены')
    await call.message.answer('Выберите действие:', reply_markup=cards_kb())

    db_session.query(Requisite).filter(Requisite.user_id == call.from_user.id).delete()
    db_session.commit()


@router.callback_query(F.data == 'my_cards')
async def my_cards_handler(call: CallbackQuery, db_session: Session):
    trader = db_session.query(Trader).get(call.from_user.id)
    reqs = trader.requisites

    text = f'Подключенные реквизиты:\n{format_requisites(reqs)}'

    await call.message.edit_text(text, reply_markup=back_cards_kb())


@router.message(F.text == 'Торговля 📈')
async def trader_trade_handler(update: Message, db_session: Session):
    trader = db_session.query(Trader).get(update.from_user.id)

    await update.answer('Торговля', reply_markup=trade_kb(trader.is_active))


@router.callback_query(F.data == 'trade')
async def trade_handler(call: CallbackQuery, db_session: Session):
    trader: Trader = db_session.query(Trader).get(call.from_user.id)
    trader.is_active = int(not trader.is_active)
    db_session.commit()

    await call.message.edit_text('Торговля', reply_markup=trade_kb(trader.is_active))


@router.callback_query(F.data == 'app')
@router.message(F.text == 'Приложение 📱')
async def trader_app_menu_handler(update: Message | CallbackQuery):
    if isinstance(update, CallbackQuery):
        func = update.message.edit_text
    else:
        func = update.answer

    await func('Выберите действие:', reply_markup=app_kb())


@router.callback_query(F.data == 'app_code')
async def app_code_handler(call: CallbackQuery, db_session: Session):
    settings = db_session.query(Settings).first()
    await call.message.edit_text(
        f'Код доступа для приложения: <code>{settings.api_key}</code>',
        reply_markup=back_app_kb()
    )


@router.callback_query(F.data == 'download_app')
async def download_app_handler(call: CallbackQuery):
    await call.message.edit_text('Тут будет APK-файл приложения', reply_markup=back_app_kb())
