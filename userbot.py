import asyncio
import os
from datetime import datetime

import requests
from pyrogram.handlers import MessageHandler
from pyrogram.methods.utilities.idle import idle
from pyrogram.types import Message

from tgbot.data.loader import Session, bot
from tgbot.services.database import Trader, Trade, Settings
from tgbot.utils.curs import get_course
from pyrogram import filters, Client
import platform

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

api_id = 27378538
api_hash = '99ebeab789ef9c139fe233b32f436abb'
apps = []


async def new_trade_handler(client, message: Message):
    trade_id = int(message.text.split(' ')[2])
    amount = int(message.text.split(' ')[4])

    btc_amount = round(amount / get_course(), 8)

    requests.get('http://localhost:8081/new_trade',
                 params={
                     'trade_id': trade_id, 'rub_amount': amount, 'btc_amount': btc_amount, 'account_id': client.me.id
                 })


async def finish_trade_handler(client, message: Message):
    trade_id = int(message.text.split(' ')[2])
    amount_rub = int(message.text.split(' ')[4])

    requests.get('http://localhost:8081/finish_trade',
                 params={'trade_id': trade_id, 'rub_amount': amount_rub, 'account_id': client.me.id})


async def missed_handler(client, message: Message):
    requests.get('http://localhost:8081/missed_trade',
                 params={'text': message.text, 'account_id': client.me.id})


new_sessions = input('Enter new sessions or nothing:\n').split()
all_sessions = [i.split('.')[0] for i in os.listdir('sessions') if i.endswith('.session')] + new_sessions

for session in all_sessions:
    session = 'sessions/' + session
    print(session)
    app = Client(session, api_id, api_hash)
    app.add_handler(
        MessageHandler(
            new_trade_handler, filters.chat('proverkakopilka4_bot') & filters.regex(r'🔥Создана новая сделка.+ ')
        )
    )
    app.add_handler(
        MessageHandler(
            finish_trade_handler, filters.chat('proverkakopilka4_bot') & filters.regex(r'✅Получен платеж.+ ')
        )
    )
    app.add_handler(
        MessageHandler(
            missed_handler, filters.chat('proverkakopilka4_bot') & filters.regex(r'❌Получен платеж на сумму.+')
        )
    )
    apps.append(app)
    app.start()
    print(app.me.id)

idle()
