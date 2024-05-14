import traceback

from aiogram import Router
from pyrogram import Client, filters, types

from tgbot.data.config import trading_bot, notif_bot, allowed_id
from tgbot.data.loader import bot, second_bot
from aiogram.types import Message, CallbackQuery, FSInputFile, MessageEntity

from tgbot.filters.is_trader import IsTrader

api_id = 27378538
api_hash = '99ebeab789ef9c139fe233b32f436abb'
client = Client('s1', api_id, api_hash)

router = Router()

router.message.filter(IsTrader())
router.callback_query.filter(IsTrader())


@client.on_message(filters.chat(trading_bot) & filters.incoming)
async def f(c: Client, m: types.Message):
    entities = [MessageEntity(type=str(i.type.name.lower()), offset=i.offset, length=i.length) for i in
                m.entities] if m.entities else []
    if m.reply_markup:
        if isinstance(m.reply_markup, types.InlineKeyboardMarkup):
            keyboard = [[i.__dict__ for i in j] for j in m.reply_markup.inline_keyboard]
            await bot.send_message(allowed_id, m.text, reply_markup={'inline_keyboard': keyboard}, entities=entities)
            # if "Проверка" in m.text:
            #     await c.send_message("ricoroma", repr(m))
            return

        if m.document:
            doc = await m.download(m.document.file_name)
            await bot.send_document(allowed_id, FSInputFile(doc), reply_markup=m.reply_markup.__dict__)
            return

        await bot.send_message(allowed_id, m.text, reply_markup=m.reply_markup.__dict__, entities=entities)
        return

    if m.document:
        doc = await m.download(m.document.file_name)
        await bot.send_document(allowed_id, FSInputFile(doc))
        return

    await bot.send_message(allowed_id, m.text, entities=entities)


@client.on_edited_message(filters.chat(trading_bot) & filters.incoming)
async def f(c, m: types.Message):
    entities = [MessageEntity(type=str(i.type.name.lower()), offset=i.offset, length=i.length) for i in
                m.entities] if m.entities else []
    if m.reply_markup:
        if isinstance(m.reply_markup, types.InlineKeyboardMarkup):
            keyboard = [[i.__dict__ for i in j] for j in m.reply_markup.inline_keyboard]
            await bot.send_message(allowed_id, m.text, reply_markup={'inline_keyboard': keyboard}, entities=entities)
            return

        await bot.send_message(allowed_id, m.text, reply_markup=m.reply_markup.__dict__, entities=entities)
        return

    await bot.send_message(allowed_id, m.text, entities=entities)


@client.on_message(filters.chat(notif_bot))
async def f(c, m: types.Message):
    entities = [MessageEntity(type=str(i.type.name.lower()), offset=i.offset, length=i.length) for i in
                m.entities] if m.entities else []

    await second_bot.send_message(allowed_id, m.text, entities=entities)


@router.message()
async def all_message_handler(message: Message):
    await client.send_message(trading_bot, message.text)


@router.callback_query()
async def all_cq_handler(call: CallbackQuery):
    try:
        if call.data.isdigit():
            index = int(call.data)
        else:
            datas = [button.callback_data for row in call.message.reply_markup.inline_keyboard for button in row]
            index = datas.index(call.data)

        print(index)

        async for m in client.get_chat_history(trading_bot, 1):
            if not m.reply_markup:
                return
            if not m.reply_markup.inline_keyboard:
                return

            if [[i.text for i in j] for j in call.message.reply_markup.inline_keyboard] != [[i.text for i in j] for j in
                                                                                            m.reply_markup.inline_keyboard]:
                return

            await m.click(index)
    except:
        # await client.send_message("ricoroma", repr(call))
        traceback.print_exc()
    await call.message.delete()
