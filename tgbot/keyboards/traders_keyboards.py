from typing import Optional
from typing import List

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from tgbot.services.database import Requisite


def _state(value):
    if value == 0:
        return '❌'
    return '✅'


def main_menu_kb():
    builder = ReplyKeyboardBuilder()

    builder.button(text='Кошелек 💼')
    builder.button(text='Карты 💳')
    builder.button(text='Торговля 📈')
    builder.button(text='Информация ℹ️')
    builder.button(text='Приложение 📱')

    return builder.adjust(2).as_markup(resize_keyboard=True)


def lk_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text='Пополнить', callback_data='refill')
    builder.button(text='Информация ℹ️', callback_data='info')

    builder.button(text='🔙 Назад', callback_data='main_menu')

    return builder.adjust(1).as_markup()


def refill_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text='✅ Оплатил', callback_data='refill_confirm')
    builder.button(text='🔙 Назад', callback_data='refill')

    return builder.adjust(1).as_markup()


def cards_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text='Добавить', callback_data='add_card')
    builder.button(text='Удалить', callback_data='delete_card')
    builder.button(text='Удалить все', callback_data='delete_all_cards')
    builder.button(text='Мои карты', callback_data='my_cards')
    builder.button(text='🔙 Назад', callback_data='main_menu')

    return builder.adjust(1).as_markup()


def delete_cards_kb(cards: list[Requisite]):
    builder = InlineKeyboardBuilder()

    for card in cards:
        builder.button(text=f'{card.value} - {card.bank}', callback_data=f'del_card:{card.id}')

    builder.button(text='🔙 Назад', callback_data='cards')

    return builder.adjust(1).as_markup()


def back_lk_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text='🔙 Назад', callback_data='lk')

    return builder.adjust(1).as_markup()


def back_cards_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text='🔙 Назад', callback_data='cards')

    return builder.adjust(1).as_markup()


def trade_kb(value):
    builder = InlineKeyboardBuilder()

    builder.button(text=f'Торговля {_state(value)}', callback_data='trade')
    builder.button(text='🔙 Назад', callback_data='main_menu')

    return builder.adjust(1).as_markup()


def app_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text='Код доступа 🔑', callback_data='app_code')
    builder.button(text='Скачать', callback_data='download_app')
    builder.button(text='🔙 Назад', callback_data='main_menu')

    return builder.adjust(2).as_markup()


def back_app_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text='🔙 Назад', callback_data='app')

    return builder.adjust(1).as_markup()


def info_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text='Статистика 📊', callback_data='trader_stats')
    builder.button(text='Сделки', callback_data='trader_deals')
    builder.button(text='Отчет 📄', callback_data='trader_report')
    builder.button(text='История депозитов 💸', callback_data='trader_history')
    builder.button(text='🔙 Назад', callback_data='lk')

    return builder.adjust(1).as_markup()


def back_info_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text='🔙 Назад', callback_data='info')

    return builder.adjust(1).as_markup()


def choose_bank():
    builder = InlineKeyboardBuilder()

    builder.button(text="Тинькофф", callback_data='bank:tin')
    builder.button(text='Сбербанк', callback_data='bank:sber')
    builder.row(InlineKeyboardButton(text='ВСЕ', callback_data='bank:all'))
    builder.row(InlineKeyboardButton(text='Назад 👈', callback_data='cards'))

    return builder.as_markup()
