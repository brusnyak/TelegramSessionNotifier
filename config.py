import os
from dotenv import load_dotenv # Ensure dotenv is imported

load_dotenv()

# --- Telegram Bot Configuration ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ENABLE_TELEGRAM_NOTIFICATIONS = os.getenv("ENABLE_TELEGRAM_NOTIFICATIONS", "True").lower() == "true"


# --- Session Management Inputs ---
TIMEZONE = os.getenv("TIMEZONE", "Europe/Bratislava")

MORNING_START_H = int(os.getenv("MORNING_START_H", 6))
MORNING_START_M = int(os.getenv("MORNING_START_M", 0))
MORNING_END_H = int(os.getenv("MORNING_END_H", 10))
MORNING_END_M = int(os.getenv("MORNING_END_M", 0))
MORNING_NAME = os.getenv("MORNING_NAME", "Morning")

AFTERNOON_START_H = int(os.getenv("AFTERNOON_START_H", 13))
AFTERNOON_START_M = int(os.getenv("AFTERNOON_START_M", 0))
AFTERNOON_END_H = int(os.getenv("AFTERNOON_END_H", 16))
AFTERNOON_END_M = int(os.getenv("AFTERNOON_END_M", 0))
AFTERNOON_NAME = os.getenv("AFTERNOON_NAME", "Afternoon")
