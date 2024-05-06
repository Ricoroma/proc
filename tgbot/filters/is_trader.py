from aiogram.types import Message
from aiogram.filters import BaseFilter

from tgbot.data.config import allowed_id


class IsTrader(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user_id = message.from_user.id

        return user_id == allowed_id
