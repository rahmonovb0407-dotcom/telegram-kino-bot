import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import database as db
from config import BOT_TOKEN
from handlers.user import router as user_router
from handlers.admin import router as admin_router
from utils.subscription_middleware import SubscriptionMiddleware

# Loglarni sozlash (Professional darajada)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

async def main():
    # Ma'lumotlar bazasini avtomatik ishga tushirish (agar mavjud bo'lmasa yaratiladi)
    await db.init_db()
    logging.info("Ma'lumotlar bazasi tekshirildi va muvaffaqiyatli ishga tushirildi.")

    # Bot va Dispatcher obyektlarini yaratish
    bot = Bot(token=BOT_TOKEN)
    
    # State'larni xotirada saqlash uchun MemoryStorage (server o'chganda statelar o'chadi, lekin fsm uchun eng tezkori)
    dp = Dispatcher(storage=MemoryStorage())

    # Obunani majburiy tekshirish uchun Middleware ulash
    dp.message.middleware(SubscriptionMiddleware())
    dp.callback_query.middleware(SubscriptionMiddleware())

    # Routerlarni ulash
    # DIQQAT: Admin routerni birinchi ulash zarur, chunki admin buyruqlari user routerda filtrlanib qolmasligi lozim
    dp.include_router(admin_router)
    dp.include_router(user_router)

    # Botni polling rejimida boshlash (eski xabarlarni o'tkazib yuborgan holda)
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Bot muvaffaqiyatli ishga tushdi va xabarlarni tinglamoqda...")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot faoliyati to'xtatildi.")
