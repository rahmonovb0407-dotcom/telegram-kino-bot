import os
from dotenv import load_dotenv

# .env faylidan o'zgaruvchilarni yuklash
load_dotenv()

# Bot token va Admin ID sini olish
BOT_TOKEN = os.getenv("BOT_TOKEN", "8980753561:AAH7gN4BifDfh8eHmph1-sqG6mNhJ3muj1c")

# Admin ID int tipiga o'tkaziladi
try:
    ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))
except ValueError:
    ADMIN_ID = 123456789
