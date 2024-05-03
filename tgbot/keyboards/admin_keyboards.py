from typing import Optional
from typing import List

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def _state(value):
    if value == 0:
        return '❌'
    return '✅'


def main_admin_kb():
    builder = ReplyKeyboardBuilder()

    builder.button(text='Трейдеры 👤')
    builder.button(text='Статистика 📈')
    builder.button(text='Настройки ⚙️')

    return builder.adjust(1).as_markup(resize_keyboard=True)


def statistics_kb(traders: list[int]):
    builder = InlineKeyboardBuilder()

    for trader in traders:
        builder.button(text=f'Статистика {trader}', callback_data=f'statistics:{trader}')
    builder.button(text='🔙 Назад', callback_data='main_admin')

    return builder.adjust(1).as_markup()


def trader_statistics_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text='🔙 Назад', callback_data='statistics')

    return builder.adjust(1).as_markup()


def choose_trader_kb(traders: list[int]):
    builder = InlineKeyboardBuilder()

    for trader in traders:
        builder.button(text=f'Трейдер {trader}', callback_data=f'trader:{trader}')

    if not traders:
        builder.button(text='Выпустить ссылку', callback_data='create_link')

    builder.button(text='🔙 Назад', callback_data='main_admin')

    return builder.adjust(1).as_markup()


def admin_trader_menu(active):
    builder = InlineKeyboardBuilder()

    builder.button(text=f'Статус: {_state(active)}', callback_data='no_button')
    builder.button(text='Реквизиты', callback_data='admin_trader_requisites')
    builder.button(text='Управление', callback_data='admin_trader_management')
    builder.button(text='🔙 Назад', callback_data='admin_traders')

    return builder.adjust(1).as_markup()


def admin_trader_status_kb(active, trader_id: int):
    builder = InlineKeyboardBuilder()

    if active:
        builder.button(text='Выключить торговлю', callback_data='trader_status:0')
    else:
        builder.button(text='Включить торговлю', callback_data='trader_status:1')

    builder.button(text='🔙 Назад', callback_data=f'trader:{trader_id}')

    return builder.adjust(1).as_markup()


def admin_requisites_kb(requisites: list[str], trader_id: int):
    builder = InlineKeyboardBuilder()

    for requisite in requisites:
        builder.button(text=requisite, callback_data=f'del_requisite:{requisite}')

    builder.button(text='🔙 Назад', callback_data=f'trader:{trader_id}')

    return builder.adjust(1).as_markup()


def admin_management_kb(active, trader_id: int):
    builder = InlineKeyboardBuilder()

    if active:
        builder.button(text='Деактивировать', callback_data='trader_status:0')
    else:
        builder.button(text='Активировать', callback_data='trader_status:1')

    builder.button(text='Изменить баланс', callback_data='trader_change_balance')
    builder.button(text='Привязать аккаунт', callback_data='add_account')
    builder.button(text='Удалить трейдера', callback_data='trader_delete')

    builder.button(text='🔙 Назад', callback_data=f'trader:{trader_id}')

    return builder.adjust(1).as_markup()


def trader_delete_confirm_kb():
    builder = InlineKeyboardBuilder()

    builder.button(text='✅ Удалить', callback_data='trader_delete_confirm')
    builder.button(text='❌ Отмена', callback_data='admin_trader_management')

    return builder.adjust(1).as_markup()


def trader_refill_confirm(trader_id, amount):
    builder = InlineKeyboardBuilder()
    builder.button(text='✅ Подтверждаю оплату', callback_data=f'refill_confirmed:{trader_id}:{amount}')

    return builder.adjust(1).as_markup()


def settings_kb():
    builder = InlineKeyboardBuilder()

    builder.button(text='Изменить API ключ', callback_data='change:api_key')
    builder.button(text='Изменить адрес пополнения', callback_data='change:refill_address')
    builder.button(text='🔙 Назад', callback_data='main_admin')

    return builder.adjust(1).as_markup()


def back_settings_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text='🔙 Назад', callback_data='settings')

    return builder.adjust(1).as_markup()


def cancel_change_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text='Отмена', callback_data='cancel_change')

    return builder.adjust(1).as_markup()
