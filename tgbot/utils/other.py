import datetime
from typing import Type

from tgbot.services.database import Requisite


def format_trades(all_trades):
    now = datetime.datetime.now()
    last_trades = [
        i for i in all_trades if datetime.datetime.strptime(
            i.date,
            '%Y-%m-%d %H:%M:%S') >= datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
    ]
    total_sum = sum([i.amount for i in all_trades])
    daily_sum = sum([i.amount for i in last_trades])

    text = f'Статистика за сегодня:\n• Сделок: {len(last_trades) or "Нет сделок"}\n• Сумма сделок: {daily_sum or 0}\n' \
           f'Общая статистика:\n• Сделок: {len(all_trades) or "Нет сделок"}\n• Сумма сделок: {total_sum or 0}'

    return text


def format_requisites(requisites: list[Type[Requisite]]):
    text = ''
    for req in requisites:
        text += f'{req.value} - <i>{req.bank}</i>\n'

    return text