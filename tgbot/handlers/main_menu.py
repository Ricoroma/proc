from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.utils.formatting import Text
from aiogram.filters import Command, CommandStart, CommandObject
from sqlalchemy.orm import Session

from tgbot.data import loader
from tgbot.data.loader import bot, links
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from tgbot.keyboards.traders_keyboards import main_menu_kb

from tgbot.services.database import User, Trader

router = Router()


@router.message(CommandStart(deep_link=True))
async def start_handler(update: Message, db_session: Session, command: CommandObject):
    trader = db_session.query(Trader).get(update.from_user.id)
    if trader:
        await update.answer('Вы уже зарегистрированы')
    else:
        code = int(command.args)
        if code in links:
            trader = Trader(user_id=update.from_user.id)
            db_session.add(trader)
            db_session.commit()

            await update.answer('Вы зарегистрированы', reply_markup=main_menu_kb())
            links.remove(code)
        else:
            await update.answer('Для продолжения необходима регистрация. Обратитесь к администратору')
