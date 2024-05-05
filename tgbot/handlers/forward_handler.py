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
from main import client

router = Router()


@router.message()
async def all_message_handler(message: Message):
    await client.send_message('Kopilkaspbp_sbpbot', message.text)


@router.callback_query()
async def all_cq_handler(call: CallbackQuery):
    index = int(call.data)

    async for m in client.get_chat_history('Kopilkaspbp_sbpbot', 1):
        if not m.reply_markup:
            return
        if not m.reply_markup.inline_keyboard:
            return

        if [[i.text for i in j] for j in call.message.keyboard] != [[i.text for i in j] for j in
                                                                    m.reply_markup.inline_keyboard]:
            return

        await m.click(index)
