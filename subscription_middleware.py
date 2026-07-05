import logging
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable

import database as db
from utils.check_sub import check_subscription
from keyboards.inline import get_subscription_keyboard
from config import ADMIN_ID

class SubscriptionMiddleware(BaseMiddleware):
    """
    Foydalanuvchi majburiy kanallarga a'zo bo'lganini tekshiruvchi middleware.
    Adminlar uchun tekshiruv chetlab o'tiladi.
    """
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Any, # Message yoki CallbackQuery
        data: Dict[str, Any]
    ) -> Any:
        # Event turini aniqlaymiz
        if not isinstance(event, (Message, CallbackQuery)):
            return await handler(event, data)
            
        user_id = event.from_user.id
        bot = data.get("bot")
        
        # Adminni tekshirmaymiz
        if user_id == ADMIN_ID:
            return await handler(event, data)
            
        # /start komandasi, "Asosiy menu" va callback_query uchun tekshiruvni o'tkazib yuboramiz
        if isinstance(event, Message):
            if event.text and (event.text.startswith("/start") or event.text == "🏠 Asosiy menu"):
                return await handler(event, data)
        elif isinstance(event, CallbackQuery):
            if event.data == "check_subscription":
                return await handler(event, data)
                
        # Majburiy kanallarni tekshiramiz
        channels = await db.get_channels()
        if not channels:
            return await handler(event, data)
            
        is_subscribed = await check_subscription(bot, user_id, channels)
        
        if not is_subscribed:
            # Obuna bo'lmagan bo'lsa javob qaytaramiz
            if isinstance(event, Message):
                await event.answer(
                    "⚠️ Botdan foydalanish uchun quyidagi kanallarga obuna bo'lishingiz shart.",
                    reply_markup=get_subscription_keyboard(channels)
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    "⚠️ Botdan foydalanish uchun barcha kanallarga obuna bo'ling!",
                    show_alert=True
                )
            return # Handler ishga tushmaydi
            
        return await handler(event, data)
