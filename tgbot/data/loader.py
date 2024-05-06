# - *- coding: utf- 8 - *-
from aiogram import Bot
from aiogram.fsm.storage.memory import MemoryStorage

from tgbot.data.config import token, second_token

bot = Bot(token=token, parse_mode=None)
second_bot = Bot(token=second_token, parse_mode=None)
storage = MemoryStorage()
