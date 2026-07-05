from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_subscription_keyboard(channels: list) -> InlineKeyboardMarkup:
    """Majburiy kanallarga a'zo bo'lish va tekshirish inline klaviaturasi."""
    builder = InlineKeyboardBuilder()
    
    for i, channel in enumerate(channels, 1):
        clean_channel = channel.strip()
        # Agar kanal username shaklida bo'lsa (masalan @KinolarUz) t.me linki yasaladi
        if clean_channel.startswith("@"):
            url = f"https://t.me/{clean_channel[1:]}"
        elif clean_channel.startswith("-100") or clean_channel.isdigit():
            # ID bo'lsa va username bo'lmasa, uni linklash imkoni bo'lmasligi mumkin, shuning uchun dummy t.me linki
            url = "https://t.me/"
        else:
            url = f"https://t.me/{clean_channel}"
            
        builder.row(InlineKeyboardButton(text=f"📢 Kanal {i}", url=url))
        
    builder.row(InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_subscription"))
    return builder.as_markup()
