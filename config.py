import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = "sqlite:///bot.db"
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x]