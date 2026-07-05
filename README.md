# 🎬 Telegram Kino Bot (Aiogram 3.x)

Ushbu loyiha professional, ko'p funksional va SQLite ma'lumotlar bazasiga ega bo'lgan Telegram Kino Botidir. Bot foydalanuvchilarga maxsus kodlar yuborish orqali kinolarni tezkor yuklab olish imkonini beradi.

## ✨ Xususiyatlari
* **Aiogram 3.x**: Eng zamonaviy asinxron Telegram Bot freymvorki.
* **SQLite (aiosqlite)**: Ma'lumotlarni asinxron rejimda tezkor va xavfsiz saqlash.
* **Majburiy obuna**: Kanallarga a'zo bo'lmaguncha foydalanuvchiga botdan foydalanishga ruxsat bermaydi (middleware orqali boshqariladi).
* **FSM (Finite State Machine)**: Kino qo'shish, kino o'chirish va majburiy kanallar qo'shish bosqichli boshqaruvi.
* **Admin Panel**: Faqat belgilangan `ADMIN_ID` ega foydalanuvchilar kirishi va kinolar, kanallarni hamda statistikani boshqarishi mumkin.
* **Video Fayl ID**: Kinolarni qayta-qayta yuklamasdan Telegram Serverlaridagi `file_id` orqali tezkor va trafixiz yuborish.

---

## 📁 Loyiha Tuzilishi (MVC)
```
/telegram_bot
├── /handlers           # Xabarlarni boshqaruvchilar (Handlers)
│   ├── user.py         # Oddiy foydalanuvchi menyusi va qidiruv tizimi
│   └── admin.py        # Admin paneli (Kino/kanal boshqaruvi va statistika)
├── /keyboards          # Tugmalar (Keyboards)
│   ├── reply.py        # Asosiy reply tugmalar (Menu)
│   └── inline.py       # Obuna bo'lish va tekshirish inline tugmalari
├── /states             # FSM holatlari (States)
│   ├── movie.py        # Kinolar boshqaruvi holatlari
│   └── channel.py      # Kanallar boshqaruvi holatlari
├── /utils              # Yordamchi funktsiyalar (Utils)
│   ├── check_sub.py    # Kanalga a'zolikni tekshiruvchi asinxron funksiya
│   └── subscription_middleware.py # Majburiy obunani filtrlovchi Middleware
├── .env.example        # Atrof-muhit o'zgaruvchilari namunasi
├── config.py           # Bot sozlamalari yuklanadigan modul
├── database.py         # SQLite CRUD asinxron moduli (Ma'lumotlar bazasi)
├── main.py             # Botni ishga tushiruvchi asosiy fayl
├── requirements.txt    # Kerakli Python kutubxonalari
└── README.md           # Qo'llanma (Ushbu fayl)
```

---

## 🚀 Mahalliydan Ishga Tushirish

### 1. Python va Kutubxonalarni O'rnatish
Kompyuteringizda Python 3.10 yoki undan yuqori versiya o'rnatilgan bo'lishi lozim.

```bash
# Kutubxonalarni o'rnatish
pip install -r requirements.txt
```

### 2. Atrof-muhitni Sozlash
Loyiha papkasida `.env` faylini yarating va quyidagi o'zgaruvchilarni kiriting:

```env
BOT_TOKEN=8980753561:AAH7gN4BifDfh8eHmph1-sqG6mNhJ3muj1c
ADMIN_ID=123456789  # O'zingizning Telegram ID'ingiz (buni @userinfobot orqali bilishingiz mumkin)
```

### 3. Botni Ishga Tushirish
```bash
python main.py
```
*Eslatma: Bot ilk bor ishga tushganda `bot.db` SQLite faylini avtomatik tarzda yaratadi va jadvallarni sozlaydi.*

---

## ☁️ Bepul Serverlarga Joylash (Deploy)

Loyiha istalgan PaaS platformalarida (Render, Railway, Koyeb) ishlashga to'liq tayyorlangan.

### 🛠 Umumiy Sozlamalar:
1. **GitHub Repozitoriyasi**: Kodlarni o'zingizning shaxsiy GitHub repozitoriyangizga yuklang (faqat `/telegram_bot` tarkibini).
2. **Environment Variables**: Server paneli orqali quyidagi o'zgaruvchilarni kiriting:
   * `BOT_TOKEN`
   * `ADMIN_ID`
3. **Start Command**: Botni ishga tushirish uchun start buyrug'ini sozlang:
   ```bash
   python main.py
   ```

### 1. Koyeb platformasiga joylash (Tavsiya etiladi - tekin)
* Koyeb saytidan ro'yxatdan o'ting va GitHub repozitoriyangizni ulang.
* **App Type** sifatida **Worker** ni tanlang (chunki web-port ochish shart emas).
* Atrof-muhit o'zgaruvchilarini (Variables) kiriting.
* Joylash tugmasini bosing, u avtomatik ravishda docker qurib botni ishga tushiradi.

### 2. Render platformasiga joylash
* Render.com ga kiring va yangi **Background Worker** xizmatini yarating.
* GitHub'ingizni ulang.
* Build Command sifatida `pip install -r requirements.txt` kiriting.
* Start Command sifatida `python main.py` kiriting.
* Advanced bo'limidan `BOT_TOKEN` va `ADMIN_ID` o'zgaruvchilarini kiriting.

---

## 📝 Ma'lumotlar Bazasi Strukturasi

### `users` jadvali
* `id` (INTEGER PRIMARY KEY)
* `telegram_id` (INTEGER UNIQUE) — Foydalanuvchining Telegram ID si.
* `fullname` (TEXT) — Ism va familiyasi.
* `username` (TEXT) — Telegram username.
* `date` (TEXT) — Ro'yxatdan o'tgan sanasi va vaqti.

### `movies` jadvali
* `id` (INTEGER PRIMARY KEY)
* `code` (TEXT UNIQUE) — Kino kodi (masalan: 1250).
* `title` (TEXT) — Kino nomi.
* `description` (TEXT) — Kino haqida ma'lumot (tavsif).
* `video_file_id` (TEXT) — Telegram serverlaridagi video fayl ID si.

### `channels` jadvali
* `id` (INTEGER PRIMARY KEY)
* `channel_id` (TEXT UNIQUE) — Majburiy kanal username'i (masalan: `@KinolarUz`).
