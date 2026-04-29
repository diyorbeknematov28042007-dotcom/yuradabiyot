from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
from database.db import add_user
from keyboards.keyboards import subscription_kb


class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user = None
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user
            if event.data == "check_subscription":
                return await handler(event, data)

        if user:
            await add_user(user.id, user.username or "", user.full_name or "")

        return await handler(event, data)


async def check_user_subscribed(bot, user_id: int):
    from database.db import get_mandatory_channels
    channels = await get_mandatory_channels()
    if not channels:
        return True, []

    not_subscribed = []
    for ch in channels:
        try:
            # @ belgisini qo'shish
            channel_id = ch["id"]
            if not channel_id.startswith("-") and not channel_id.startswith("@"):
                channel_id = "@" + channel_id

            member = await bot.get_chat_member(channel_id, user_id)
            if member.status in ("left", "kicked", "banned"):
                not_subscribed.append(ch)
        except Exception as e:
            # Kanal topilmasa yoki xato bo'lsa — o'tkazib yuborish
            print(f"Kanal tekshirishda xato {ch['id']}: {e}")
            not_subscribed.append(ch)

    return len(not_subscribed) == 0, not_subscribed
