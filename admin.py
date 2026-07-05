from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import database as db
from config import ADMIN_ID
from keyboards.reply import get_admin_keyboard, get_main_keyboard, get_back_keyboard
from states.movie import MovieStates
from states.channel import ChannelStates

router = Router()

# Faqat ADMIN_ID ushbu routerni ishlata oladi
router.message.filter(F.from_user.id == ADMIN_ID)

@router.message(Command("admin"))
@router.message(F.text == "Admin Panel")
async def cmd_admin(message: Message, state: FSMContext):
    """Admin panelga kirish."""
    await state.clear()
    await message.answer(
        "⚙️ **Admin paneliga xush kelibsiz!**\n\nKerakli amalni tanlang:",
        reply_markup=get_admin_keyboard(),
        parse_mode="Markdown"
    )

# --- KINO QO'SHISH BOSQICHLARI (FSM) ---

@router.message(F.text == "➕ Kino qo'shish")
async def start_add_movie(message: Message, state: FSMContext):
    """Kino qo'shishni boshlash (kod so'rash)."""
    await state.set_state(MovieStates.waiting_for_add_code)
    await message.answer(
        "📝 **Kino kodi:**\n\nMisol uchun: `1250`",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )

@router.message(MovieStates.waiting_for_add_code)
async def process_add_code(message: Message, state: FSMContext):
    """Kino kodi kiritilganda."""
    code = message.text.strip()
    
    if code == "🏠 Asosiy menu":
        await state.clear()
        await message.answer("Bosh menyuga qaytdingiz:", reply_markup=get_main_keyboard())
        return
        
    # Kod bazada bor-yo'qligini tekshirish
    exists = await db.get_movie(code)
    if exists:
        await message.answer(
            "❌ Bu koddagi kino allaqachon bazada mavjud!\n\nIltimos, boshqa kod kiriting:",
            reply_markup=get_back_keyboard()
        )
        return
        
    await state.update_data(code=code)
    await state.set_state(MovieStates.waiting_for_add_title)
    await message.answer(
        "🎬 **Kino nomini kiriting:**",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )

@router.message(MovieStates.waiting_for_add_title)
async def process_add_title(message: Message, state: FSMContext):
    """Kino nomi kiritilganda."""
    title = message.text.strip()
    
    if title == "🏠 Asosiy menu":
        await state.clear()
        await message.answer("Bosh menyuga qaytdingiz:", reply_markup=get_main_keyboard())
        return
        
    await state.update_data(title=title)
    await state.set_state(MovieStates.waiting_for_add_desc)
    await message.answer(
        "📝 **Kino tavsifini (opisaniya) kiriting:**",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )

@router.message(MovieStates.waiting_for_add_desc)
async def process_add_desc(message: Message, state: FSMContext):
    """Kino tavsifi kiritilganda."""
    desc = message.text.strip()
    
    if desc == "🏠 Asosiy menu":
        await state.clear()
        await message.answer("Bosh menyuga qaytdingiz:", reply_markup=get_main_keyboard())
        return
        
    await state.update_data(description=desc)
    await state.set_state(MovieStates.waiting_for_add_video)
    await message.answer(
        "🎥 **Kino videosini yuboring (MP4 yoki Video fayl):**",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )

@router.message(MovieStates.waiting_for_add_video)
async def process_add_video(message: Message, state: FSMContext):
    """Kino videosi yuborilganda."""
    # Agar foydalanuvchi adashib matn yozgan bo'lsa
    if message.text == "🏠 Asosiy menu":
        await state.clear()
        await message.answer("Bosh menyuga qaytdingiz:", reply_markup=get_main_keyboard())
        return
        
    if not message.video:
        await message.answer(
            "❌ Iltimos, faqat video fayl yuboring!",
            reply_markup=get_back_keyboard()
        )
        return
        
    video_file_id = message.video.file_id
    data = await state.get_data()
    
    # Bazaga yozamiz
    success = await db.add_movie(
        code=data["code"],
        title=data["title"],
        description=data["description"],
        video_file_id=video_file_id
    )
    
    await state.clear()
    
    if success:
        await message.answer(
            "✅ **Kino muvaffaqiyatli saqlandi!**\n\nKino kodi: " + data["code"],
            reply_markup=get_admin_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            "❌ Kinoni saqlashda xatolik yuz berdi (bazaviy xato).",
            reply_markup=get_admin_keyboard()
        )

# --- KINO O'CHIRISH BOSQICHI (FSM) ---

@router.message(F.text == "🗑 Kino o'chirish")
async def start_delete_movie(message: Message, state: FSMContext):
    """Kino o'chirishni boshlash."""
    await state.set_state(MovieStates.waiting_for_delete_code)
    await message.answer(
        "🗑 **O'chiriladigan kino kodini yuboring:**",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )

@router.message(MovieStates.waiting_for_delete_code)
async def process_delete_movie(message: Message, state: FSMContext):
    """Kino kodi o'chirish uchun kiritilganda."""
    code = message.text.strip()
    
    if code == "🏠 Asosiy menu":
        await state.clear()
        await message.answer("Bosh menyuga qaytdingiz:", reply_markup=get_main_keyboard())
        return
        
    success = await db.delete_movie(code)
    await state.clear()
    
    if success:
        await message.answer(
            f"✅ Kod: `{code}` bo'lgan kino bazadan muvaffaqiyatli o'chirildi!",
            reply_markup=get_admin_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            "❌ Bunday kod topilmadi.",
            reply_markup=get_admin_keyboard()
        )

# --- STATISTIKA ---

@router.message(F.text == "📊 Statistika")
async def show_statistics(message: Message):
    """Bot statistikasini chiqarish."""
    users_count = await db.get_users_count()
    movies_count = await db.get_movies_count()
    today_users = await db.get_today_users_count()
    
    stat_msg = (
        "📊 **Bot Statistikasi:**\n\n"
        f"👤 **Jami foydalanuvchilar soni:** {users_count}\n"
        f"🎬 **Jami kinolar soni:** {movies_count}\n"
        f"📅 **Bugungi foydalanuvchilar:** {today_users}\n"
        f"📈 **Jami start bosganlar:** {users_count}\n"
    )
    await message.answer(
        stat_msg,
        reply_markup=get_admin_keyboard(),
        parse_mode="Markdown"
    )

# --- MAJBURIY KANALLAR BOSQICHLARI (FSM) ---

@router.message(F.text == "➕ Majburiy kanal qo'shish")
async def start_add_channel(message: Message, state: FSMContext):
    """Kanal qo'shishni boshlash."""
    await state.set_state(ChannelStates.waiting_for_channel_id)
    await message.answer(
        "📢 **Kanal username yoki ID sini yuboring.**\n\nMasalan: `@KinolarUz` yoki `-1001234567890`",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )

@router.message(ChannelStates.waiting_for_channel_id)
async def process_add_channel(message: Message, state: FSMContext):
    """Kanal kiritilganda."""
    channel_id = message.text.strip()
    
    if channel_id == "🏠 Asosiy menu":
        await state.clear()
        await message.answer("Bosh menyuga qaytdingiz:", reply_markup=get_main_keyboard())
        return
        
    if not (channel_id.startswith("@") or channel_id.startswith("-100") or channel_id.isdigit()):
        await message.answer(
            "❌ Noto'g'ri format. Iltimos, `@` bilan boshlanuvchi username yoki `-100` bilan boshlanuvchi kanal ID kiriting:",
            reply_markup=get_back_keyboard()
        )
        return
        
    success = await db.add_channel(channel_id)
    await state.clear()
    
    if success:
        await message.answer(
            f"✅ Majburiy kanal muvaffaqiyatli qo'shildi: `{channel_id}`",
            reply_markup=get_admin_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            "❌ Bu kanal allaqachon qo'shilgan yoki xatolik yuz berdi.",
            reply_markup=get_admin_keyboard()
        )

@router.message(F.text == "➖ Majburiy kanalni o'chirish")
async def start_delete_channel(message: Message, state: FSMContext):
    """Kanal o'chirishni boshlash (kanallar ro'yxatini chiqarib)."""
    channels = await db.get_channels()
    
    if not channels:
        await message.answer(
            "📭 Hozirda majburiy kanallar qo'shilmagan.",
            reply_markup=get_admin_keyboard()
        )
        return
        
    channels_str = "\n".join([f"• `{ch}`" for ch in channels])
    await state.set_state(ChannelStates.waiting_for_delete_channel)
    await message.answer(
        f"📢 **Hozirgi majburiy kanallar ro'yxati:**\n\n{channels_str}\n\n"
        f"O'chirmoqchi bo'lgan kanal username yoki ID sini kiriting:",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )

@router.message(ChannelStates.waiting_for_delete_channel)
async def process_delete_channel(message: Message, state: FSMContext):
    """Kanal o'chirish kodi kiritilganda."""
    channel_id = message.text.strip()
    
    if channel_id == "🏠 Asosiy menu":
        await state.clear()
        await message.answer("Bosh menyuga qaytdingiz:", reply_markup=get_main_keyboard())
        return
        
    success = await db.delete_channel(channel_id)
    await state.clear()
    
    if success:
        await message.answer(
            f"✅ Kanal bazadan o'chirildi: `{channel_id}`",
            reply_markup=get_admin_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            "❌ Bunday kanal topilmadi. Iltimos, ro'yxatdagidek yozing.",
            reply_markup=get_admin_keyboard()
        )
