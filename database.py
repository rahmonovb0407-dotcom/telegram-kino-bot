import aiosqlite
import datetime
import os

DB_NAME = "bot.db"

async def init_db():
    """Bot ishga tushganda ma'lumotlar bazasini va jadvallarni yaratadi."""
    async with aiosqlite.connect(DB_NAME) as db:
        # Foydalanuvchilar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                fullname TEXT,
                username TEXT,
                date TEXT
            )
        """)
        
        # Kinolar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE,
                title TEXT,
                description TEXT,
                video_file_id TEXT
            )
        """)
        
        # Majburiy kanallar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT UNIQUE
            )
        """)
        await db.commit()

# --- FOYDALANUVCHILAR BILAN ISHLASH ---

async def add_user(telegram_id: int, fullname: str, username: str):
    """Yangi foydalanuvchini bazaga qo'shadi yoki ma'lumotlarini yangilaydi."""
    async with aiosqlite.connect(DB_NAME) as db:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            await db.execute(
                "INSERT INTO users (telegram_id, fullname, username, date) VALUES (?, ?, ?, ?)",
                (telegram_id, fullname, username, now)
            )
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            # Foydalanuvchi allaqachon mavjud bo'lsa, ism va username yangilanadi
            await db.execute(
                "UPDATE users SET fullname = ?, username = ? WHERE telegram_id = ?",
                (fullname, username, telegram_id)
            )
            await db.commit()
            return False

async def get_user(telegram_id: int):
    """Foydalanuvchini telegram_id bo'yicha bazadan qidiradi."""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
            return await cursor.fetchone()

async def get_users_count():
    """Jami foydalanuvchilar sonini qaytaradi."""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

async def get_today_users_count():
    """Bugun qo'shilgan foydalanuvchilar sonini qaytaradi."""
    async with aiosqlite.connect(DB_NAME) as db:
        today_start = datetime.datetime.now().strftime("%Y-%m-%d") + " 00:00:00"
        async with db.execute("SELECT COUNT(*) FROM users WHERE date >= ?", (today_start,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

# --- KINOLAR BILAN ISHLASH ---

async def add_movie(code: str, title: str, description: str, video_file_id: str):
    """Kino bazaga qo'shadi. Agar kod takrorlansa False qaytaradi."""
    async with aiosqlite.connect(DB_NAME) as db:
        try:
            await db.execute(
                "INSERT INTO movies (code, title, description, video_file_id) VALUES (?, ?, ?, ?)",
                (code, title, description, video_file_id)
            )
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            return False

async def get_movie(code: str):
    """Kino kodi bo'yicha kinoni qidiradi."""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM movies WHERE code = ?", (code,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "code": row[1],
                    "title": row[2],
                    "description": row[3],
                    "video_file_id": row[4]
                }
            return None

async def delete_movie(code: str):
    """Kino kodi bo'yicha kinoni o'chiradi."""
    async with aiosqlite.connect(DB_NAME) as db:
        # Kino mavjudligini tekshirish
        async with db.execute("SELECT id FROM movies WHERE code = ?", (code,)) as cursor:
            if not await cursor.fetchone():
                return False
        
        await db.execute("DELETE FROM movies WHERE code = ?", (code,))
        await db.commit()
        return True

async def get_movies_count():
    """Jami kinolar sonini qaytaradi."""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT COUNT(*) FROM movies") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

# --- MAJBURIY KANALLAR BILAN ISHLASH ---

async def add_channel(channel_id: str):
    """Majburiy obuna kanalini qo'shadi."""
    async with aiosqlite.connect(DB_NAME) as db:
        try:
            await db.execute("INSERT INTO channels (channel_id) VALUES (?)", (channel_id,))
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            return False

async def delete_channel(channel_id: str):
    """Majburiy obuna kanalini o'chiradi."""
    async with aiosqlite.connect(DB_NAME) as db:
        # Kanal mavjudligini tekshirish
        async with db.execute("SELECT id FROM channels WHERE channel_id = ?", (channel_id,)) as cursor:
            if not await cursor.fetchone():
                return False
        
        await db.execute("DELETE FROM channels WHERE channel_id = ?", (channel_id,))
        await db.commit()
        return True

async def get_channels():
    """Hamma majburiy kanallarni ro'yxatini qaytaradi."""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT channel_id FROM channels") as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
