from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from tgbot.data.config import admin_ids
from tgbot.data.loader import Session
from tgbot.services.database import User, Trader


class DatabaseMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        db_session = Session()
        # event_user = data['event_from_user']
        # user = db_session.query(Trader).filter(Trader.user_id == event_user.id).first()
        #
        # if not user:
        #     user = Trader(user_id=event_user.id)
        #     db_session.add(user)
        #     db_session.commit()

        data['db_session'] = db_session

        result = await handler(event, data)

        db_session.close()
        return result
