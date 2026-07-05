import logging
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbidden

async def check_subscription(bot: Bot, user_id: int, channels: list) -> bool:
    """
    Foydalanuvchini barcha majburiy kanallarga obunali bo'lganini tekshiradi.
    Agar obuna bo'lmagan bo'lsa, False qaytaradi.
    """
    if not channels:
        return True
        
    for channel in channels:
        channel_id = channel.strip()
        try:
            member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            if member.status in ["creator", "administrator", "member", "restricted"]:
                continue
            else:
                return False
        except (TelegramBadRequest, TelegramForbidden) as e:
            # Agar bot kanalda administrator bo'lmasa yoki kanal topilmasa xatolik beradi
            logging.warning(f"Kanal obunasini tekshirishda xatolik ({channel_id}): {e}")
            # Xatolik yuz berganda obunani o'tib ketishiga yo'l qo'ymaslik uchun False qaytaramiz
            return False
        except Exception as e:
            logging.error(f"Kanal obunasini tekshirishda kutilmagan xatolik: {e}")
            return False
            
    return True
