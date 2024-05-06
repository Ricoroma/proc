import asyncio

from aiogram import Bot
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputFile, FSInputFile, MessageEntity
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from pyrogram import Client, filters

from pyrogram.handlers import MessageHandler
from pyrogram.methods.utilities.idle import idle
from pyrogram.types import Message, InlineKeyboardMarkup
from pyrogram import types
import platform

from tgbot.data.config import token

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

api_id = 27378538
api_hash = '99ebeab789ef9c139fe233b32f436abb'
client = Client('s1', api_id, api_hash)
bot = Bot(token=token)


@client.on_message(filters.chat('Kopilkaspbp_sbpbot') & filters.incoming)
async def f(c: Client, m: Message):
    entities = [MessageEntity(type=str(i.type.name.lower()), offset=i.offset, length=i.length) for i in
                m.entities] if m.entities else []
    print(entities)
    if m.reply_markup:
        if isinstance(m.reply_markup, types.InlineKeyboardMarkup):
            keyboard = [[i.__dict__ for i in j] for j in m.reply_markup.inline_keyboard]
            await bot.send_message(c.me.id, m.text, reply_markup={'inline_keyboard': keyboard}, entities=entities)
            return

        if m.document:
            doc = await m.download(m.document.file_name)
            await bot.send_document(c.me.id, FSInputFile(doc), reply_markup=m.reply_markup.__dict__)
            return

        await bot.send_message(c.me.id, m.text, reply_markup=m.reply_markup.__dict__, entities=entities)
        return

    await bot.send_message(c.me.id, m.text, entities=entities)


@client.on_edited_message(filters.chat('Kopilkaspbp_sbpbot') & filters.incoming)
async def f(c, m: Message):
    entities = [MessageEntity(type=str(i.type.name.lower()), offset=i.offset, length=i.length) for i in
                m.entities] if m.entities else []
    if m.reply_markup:
        if isinstance(m.reply_markup, types.InlineKeyboardMarkup):
            keyboard = [[i.__dict__ for i in j] for j in m.reply_markup.inline_keyboard]
            await bot.send_message(c.me.id, m.text, reply_markup={'inline_keyboard': keyboard}, entities=entities)
            return

        await bot.send_message(c.me.id, m.text, reply_markup=m.reply_markup.__dict__, entities=entities)
        return

    await bot.send_message(c.me.id, m.text, entities=entities)


# def form_inline_keyboard(kb:InlineKeyboardMarkup):


client.run()
