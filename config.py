import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS_RAW = os.getenv("ADMIN_IDS", "6206932601,8013328081")
ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_RAW.split(",") if x.strip()]
DATABASE_URL = os.getenv("DATABASE_URL", "")
