from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

import database as db
from keyboards.reply import get_main_keyboard, get_back_keyboard
from keyboards.inline import get_subscription_keyboard
from utils.check_sub import check_subscription
from states.movie import MovieStates

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot, state: FSMContext):
    """/start komandasi bosilganda ishlaydi. Obunani tekshiradi va foydalanuvchini ro'yxatga oladi."""
    await state.clear()
    user_id = message.from_user.id
    fullname = message.from_user.full_name or "Foydalanuvchi"
    username = message.from_user.username or "username_yoq"
    
    # Ma'lumotlar bazasiga foydalanuvchini qo'shish
    await db.add_user(user_id, fullname, username)
    
    # Majburiy obuna kanallarini olish
    channels = await db.get_channels()
    
    # Obunani tekshirish
    is_subscribed = await check_subscription(bot, user_id, channels)
    
    if not is_subscribed:
        await message.answer(
            "📢 Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling.",
            reply_markup=get_subscription_keyboard(channels)
        )
    else:
        await message.answer(
            f"Salom, {fullname}! Kino botimizga xush kelibsiz.\n\n"
            f"Kino tomosha qilish uchun 🎬 **Kino kodini kiritish** tugmasini bosing yoki to'g'ridan-to'g'ri kodni yuboring.",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )

@router.callback_query(F.data == "check_subscription")
async def cb_check_subscription(callback: CallbackQuery, bot: Bot, state: FSMContext):
    """Obunani tekshirish inline tugmasi bosilganda ishlaydi."""
    user_id = callback.from_user.id
    fullname = callback.from_user.full_name or "Foydalanuvchi"
    username = callback.from_user.username or "username_yoq"
    
    channels = await db.get_channels()
    is_subscribed = await check_subscription(bot, user_id, channels)
    
    if is_subscribed:
        # Foydalanuvchini bazaga qo'shish (yana bir bor)
        await db.add_user(user_id, fullname, username)
        
        await callback.message.delete()
        await callback.message.answer(
            "✅ Tabriklaymiz! Siz barcha kanallarga muvaffaqiyatli a'zo bo'ldingiz.",
            reply_markup=get_main_keyboard()
        )
        await callback.answer()
    else:
        await callback.answer(
            "❌ Siz hali barcha kanallarga obuna bo'lmadingiz! Iltimos, qaytadan tekshirib ko'ring.",
            show_alert=True
        )

@router.message(F.text == "🏠 Asosiy menu")
async def process_back_home(message: Message, state: FSMContext):
    """Asosiy menyuga qaytish tugmasi."""
    await state.clear()
    await message.answer(
        "🏠 Siz asosiy menyudasiz. Kerakli bo'limni tanlang:",
        reply_markup=get_main_keyboard()
    )

@router.message(F.text == "🎬 Kino kodini kiritish")
async def process_kino_search_prompt(message: Message, state: FSMContext):
    """Kino kodini kiritish bo'limi boshlanganda."""
    await state.set_state(MovieStates.waiting_for_search_code)
    await message.answer(
        "🎥 Kino kodini kiriting:",
        reply_markup=get_back_keyboard()
    )

@router.message(F.text == "📂 Kinolar kanali")
async def process_movies_channel(message: Message):
    """Kino kanali havolasi yuboriladi."""
    await message.answer(
        "📢 Barcha kinolarimiz shu kanalda joylangan.\n\n🔗 [https://t.me/kanal_nomi](https://t.me/kanal_nomi)",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

@router.message(F.text == "📞 Bog'lanish")
async def process_contact(message: Message):
    """Bog'lanish ma'lumotlari."""
    await message.answer(
        "📞 Bot bo'yicha savol va takliflar bo'lsa admin bilan bog'laning:\n\n"
        "👤 Admin: @admin_username\n"
        "💬 Guruhimiz: @guruh_username",
        reply_markup=get_main_keyboard()
    )

@router.message(F.text == "ℹ️ Bot haqida")
async def process_about(message: Message):
    """Bot haqida ma'lumot."""
    await message.answer(
        "ℹ️ **Bot haqida:**\n\n"
        "Ushbu bot orqali siz istagan kinolaringizni faqatgina uning kodini "
        "yuborish orqali tezkor va bepul yuklab olishingiz mumkin!\n\n"
        "Kino qidirishni boshlash uchun bosh menyudan foydalaning.",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

@router.message(MovieStates.waiting_for_search_code)
async def process_movie_search_state(message: Message, state: FSMContext):
    """Kino kodi kiritilganda (FSM holatda)."""
    code = message.text.strip()
    
    # Asosiy menyuga qaytish bosilgan bo'lsa
    if code == "🏠 Asosiy menu":
        await state.clear()
        await message.answer("🏠 Bosh menyudasiz:", reply_markup=get_main_keyboard())
        return
        
    movie = await db.get_movie(code)
    
    if movie:
        await state.clear() # Qidiruv tugadi
        # Kinoni yuborish
        await message.answer_video(
            video=movie["video_file_id"],
            caption=f"🎬 **Kino nomi:** {movie['title']}\n\n📝 **Kino kodi:** {movie['code']}\n\nℹ️ **Tavsif:**\n{movie['description']}",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            "❌ Bunday koddagi kino topilmadi.\n\nQaytadan urinib ko'ring yoki boshqa kod yuboring:",
            reply_markup=get_back_keyboard()
        )

@router.message(F.text)
async def process_global_search(message: Message, state: FSMContext):
    """Foydalanuvchi FSM holatisiz to'g'ridan-to'g'ri kod yozsa ham qidirib beradi."""
    code = message.text.strip()
    
    # Agar raqamli yoki kod formatida bo'lsa, qidirib ko'ramiz
    movie = await db.get_movie(code)
    
    if movie:
        await message.answer_video(
            video=movie["video_file_id"],
            caption=f"🎬 **Kino nomi:** {movie['title']}\n\n📝 **Kino kodi:** {movie['code']}\n\nℹ️ **Tavsif:**\n{movie['description']}",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )
    else:
        # Agar oddiy matn bo'lsa va kino topilmasa, bot tushunmaganini bildiradi
        await message.answer(
            "❌ Bunday koddagi kino topilmadi.\n\n"
            "Iltimos, kodni to'g'ri yozganingizga ishonch hosil qiling.",
            reply_markup=get_main_keyboard()
        )
