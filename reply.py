from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Foydalanuvchilar uchun bosh menyu klaviaturasi."""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🎬 Kino kodini kiritish"),
        KeyboardButton(text="📂 Kinolar kanali")
    )
    builder.row(
        KeyboardButton(text="📞 Bog'lanish"),
        KeyboardButton(text="ℹ️ Bot haqida")
    )
    return builder.as_markup(resize_keyboard=True)

def get_back_keyboard() -> ReplyKeyboardMarkup:
    """Asosiy menyuga qaytish klaviaturasi."""
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="🏠 Asosiy menu"))
    return builder.as_markup(resize_keyboard=True)

def get_admin_keyboard() -> ReplyKeyboardMarkup:
    """Adminlar uchun boshqaruv paneli klaviaturasi."""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="➕ Kino qo'shish"),
        KeyboardButton(text="🗑 Kino o'chirish")
    )
    builder.row(KeyboardButton(text="📊 Statistika"))
    builder.row(
        KeyboardButton(text="➕ Majburiy kanal qo'shish"),
        KeyboardButton(text="➖ Majburiy kanalni o'chirish")
    )
    builder.row(KeyboardButton(text="🏠 Asosiy menu"))
    return builder.as_markup(resize_keyboard=True)
