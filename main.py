import asyncio
import logging
import sys
from contextlib import asynccontextmanager

from aiogram import Dispatcher
from aiogram.types import Update
from fastapi import FastAPI
from pyrogram import idle

from tgbot.data.config import webhook_url
from tgbot.data.loader import bot, storage
from tgbot.handlers import forward_handler
from tgbot.handlers.forward_handler import client
import platform

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

dp = Dispatcher(storage=storage)
logging.basicConfig(level=logging.INFO, stream=sys.stdout)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info('start')
    dp.include_router(forward_handler.router)
    await bot.set_webhook(webhook_url)
    await client.start()

    yield

    await idle()

    await client.stop()

    await bot.delete_webhook(drop_pending_updates=True)

    session = bot.session
    await session.close()


app = FastAPI(lifespan=lifespan)


@app.post(f"/hook")
async def process_event(update: Update):
    try:
        await dp.feed_webhook_update(bot=bot, update=update)
        return {"ok": True}
    except Exception as e:
        logging.exception("Error processing update")
