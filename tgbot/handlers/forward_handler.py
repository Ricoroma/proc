from random import randint

from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.utils.formatting import Text
from aiogram.filters import Command
from pyrogram import Client, filters, types
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

api_id = 27378538
api_hash = '99ebeab789ef9c139fe233b32f436abb'
client = Client('s1', api_id, api_hash)

router = Router()


@client.on_message(filters.chat('Kopilkaspbp_sbpbot') & filters.incoming)
async def f(c: Client, m: Message):
    if m.reply_markup:
        if isinstance(m.reply_markup, types.InlineKeyboardMarkup):
            keyboard = [[i.__dict__ for i in j] for j in m.reply_markup.inline_keyboard]
            await bot.send_message(c.me.id, m.text, reply_markup={'inline_keyboard': keyboard})
            return

        if m.document:
            doc = await m.download(m.document.file_name)
            await bot.send_document(c.me.id, FSInputFile(doc), reply_markup=m.reply_markup.__dict__)
            return

        await bot.send_message(c.me.id, m.text, reply_markup=m.reply_markup.__dict__)
        return


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

        if [[i.text for i in j] for j in call.message.reply_markup.inline_keyboard] != [[i.text for i in j] for j in
                                                                                        m.reply_markup.inline_keyboard]:
            return

        await m.click(index)
