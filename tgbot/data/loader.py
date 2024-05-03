# - *- coding: utf- 8 - *-
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from pyrogram import Client

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tgbot.data.config import token, database_path

bot = Bot(token=token, parse_mode=ParseMode.HTML)
storage = MemoryStorage()

engine = create_engine(database_path, isolation_level='AUTOCOMMIT')
engine.connect()
Session = sessionmaker(engine)
Session.configure(bind=engine)
links = []

api_id = 27378538
api_hash = '99ebeab789ef9c139fe233b32f436abb'
app = Client('first_account', api_id=api_id, api_hash=api_hash)
