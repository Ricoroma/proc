from aiogram.types import Message
from aiogram.filters import BaseFilter
from tgbot.data.loader import Session
from tgbot.services.database import Trader


class IsTrader(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user_id = message.from_user.id

        with Session() as db_session:
            return db_session.query(Trader).get(user_id) is not None
