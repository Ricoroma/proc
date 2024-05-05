import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime

from aiogram import Dispatcher
from aiogram.types import Update
from fastapi import FastAPI, Request, Depends
from pyrogram import Client, filters, idle, types
from pyrogram.types import Message

from tgbot.data.config import webhook_url
from tgbot.data.loader import bot, storage, Session
from tgbot.handlers import traders_handler, admin_handler, forward_handler
from tgbot.middlewares.database_middleware import DatabaseMiddleware
import tgbot.handlers.main_menu as main_menu
import platform

from tgbot.services.database import Trader, Trade
from sqlalchemy.orm import session

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

dp = Dispatcher(storage=storage)
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

api_id = 27378538
api_hash = '99ebeab789ef9c139fe233b32f436abb'
client = Client('s1', api_id, api_hash)


@client.on_message(filters.chat('Kopilkaspbp_sbpbot') & filters.incoming)
async def f(c: Client, m: Message):
    if m.reply_markup:
        if isinstance(m.reply_markup, types.InlineKeyboardMarkup):
            keyboard = [[i.__dict__ for i in j] for j in m.reply_markup.inline_keyboard]
            await bot.send_message(c.me.id, m.text, reply_markup={'inline_keyboard': keyboard})
            return
        await bot.send_message(c.me.id, m.text, reply_markup=m.reply_markup.__dict__)
        return

    await bot.send_message(c.me.id, m.text)


@client.on_edited_message(filters.chat('Kopilkaspbp_sbpbot') & filters.incoming)
async def f(c, m: Message):
    if m.reply_markup:
        if isinstance(m.reply_markup, types.InlineKeyboardMarkup):
            keyboard = [[i.__dict__ for i in j] for j in m.reply_markup.inline_keyboard]
            await bot.send_message(c.me.id, m.text, reply_markup={'inline_keyboard': keyboard})
            return
        await bot.send_message(c.me.id, m.text, reply_markup=m.reply_markup.__dict__)
        return

    await bot.send_message(c.me.id, m.text)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info('start')
    dp.include_router(forward_handler.router)
    dp.include_router(main_menu.router)
    dp.include_router(admin_handler.router)
    dp.include_router(traders_handler.router)

    dp.update.middleware(DatabaseMiddleware())

    await bot.set_webhook(webhook_url)
    await client.start()

    yield

    await idle()

    await client.stop()

    await bot.delete_webhook(drop_pending_updates=True)

    session = await bot.get_session()
    await session.close()


app = FastAPI(lifespan=lifespan)


def get_session():
    with Session() as db_session:
        yield db_session


@app.post(f"/hook")
async def process_event(update: Update):
    try:
        await dp.feed_webhook_update(bot=bot, update=update)
        return {"ok": True}
    except Exception as e:
        logging.exception("Error processing update")


@app.get(f'/new_trade')
async def process_new_update(account_id: int, rub_amount: int, btc_amount: float, trade_id: int,
                             db_session: session.Session = Depends(get_session)):
    trader = db_session.query(Trader).filter(Trader.account_id == account_id).first()

    if not trader:
        return 'ok'

    if trader.is_active:
        await bot.send_message(trader.user_id, f'🧨 Новая сделка: {trade_id} на {rub_amount} ₽')

        trade = Trade(
            id=trade_id,
            trader_id=trader.user_id,
            amount=btc_amount,
            date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

        db_session.add(trade)
        db_session.commit()

        return 'ok'


@app.get(f'/finish_trade')
async def process_finished_update(account_id: int, trade_id: int, rub_amount: int,
                                  db_session: session.Session = Depends(get_session)):
    trader = db_session.query(Trader).filter(Trader.account_id == account_id).first()

    if not trader:
        return 'ok'

    if trader.is_active:
        trade = db_session.query(Trade).filter(Trade.id == trade_id).first()

        await bot.send_message(trader.user_id, f'✅ Сделка {trade_id} на {rub_amount} ₽ завершена')
        trade.state = 1
        trade.date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        trader.balance = round(trader.balance - trade.amount, 8)

        db_session.commit()

        return 'ok'


@app.get(f'/missed_trade')
async def process_missed_update(account_id: int, text: str, db_session: session.Session = Depends(get_session)):
    trader = db_session.query(Trader).filter(Trader.account_id == account_id).first()

    if not trader:
        return 'ok'

    if trader.is_active:
        await bot.send_message(trader.user_id, text)

        return 'ok'
