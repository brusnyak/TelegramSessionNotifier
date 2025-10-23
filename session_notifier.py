import os
import pytz
import requests
import schedule
import time
from datetime import datetime, timedelta, UTC # Import UTC directly
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration from config.py (or .env for sensitive data) ---
# Ensure these are consistent with pine_to_python_indicator/config.py
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ENABLE_TELEGRAM_NOTIFICATIONS = os.getenv("ENABLE_TELEGRAM_NOTIFICATIONS", "True").lower() == "true"

TIMEZONE_STR = os.getenv("TIMEZONE", "Europe/Bratislava")
TIMEZONE = pytz.timezone(TIMEZONE_STR)

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

# --- Global state to track notification status ---
# This will prevent duplicate notifications for the same event
notification_sent_status = {
    "morning_start": False,
    "morning_end": False,
    "afternoon_start": False,
    "afternoon_end": False,
}

def send_telegram_message(message):
    """Sends a message to the configured Telegram chat."""
    if not ENABLE_TELEGRAM_NOTIFICATIONS:
        print("Telegram notifications are disabled.")
        return

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram bot token or chat ID is not configured.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        print(f"Telegram message sent: {message}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending Telegram message: {e}")

def get_current_time_in_timezone():
    """Returns the current time in the configured timezone."""
    # Use datetime.now(UTC) to avoid DeprecationWarning
    utc_now = datetime.now(UTC)
    return utc_now.astimezone(TIMEZONE)

def check_session_status():
    """Checks current time against session times and sends notifications."""
    global notification_sent_status
    now = get_current_time_in_timezone()
    current_time_str = now.strftime("%H:%M")
    current_date_str = now.strftime("%Y-%m-%d")

    print(f"Checking session status at {current_time_str} on {current_date_str} ({TIMEZONE_STR})")

    sessions = [
        {
            "name": MORNING_NAME,
            "start": now.replace(hour=MORNING_START_H, minute=MORNING_START_M, second=0, microsecond=0),
            "end": now.replace(hour=MORNING_END_H, minute=MORNING_END_M, second=0, microsecond=0),
            "start_key": "morning_start",
            "end_key": "morning_end",
        },
        {
            "name": AFTERNOON_NAME,
            "start": now.replace(hour=AFTERNOON_START_H, minute=AFTERNOON_START_M, second=0, microsecond=0),
            "end": now.replace(hour=AFTERNOON_END_H, minute=AFTERNOON_END_M, second=0, microsecond=0),
            "start_key": "afternoon_start",
            "end_key": "afternoon_end",
        },
    ]

    for session in sessions:
        session_name = session["name"]
        session_start = session["start"]
        session_end = session["end"]
        start_key = session["start_key"]
        end_key = session["end_key"]

        # Check for session start
        # We allow a small window (e.g., 1 minute) around the exact start/end time to trigger
        # This helps account for scheduler delays and ensures the notification is sent
        if session_start <= now < session_start + timedelta(minutes=1) and not notification_sent_status[start_key]:
            send_telegram_message(f"🔔 *{session_name} Session Started!* 🔔\nTime: {session_start.strftime('%H:%M')} {TIMEZONE_STR}")
            notification_sent_status[start_key] = True
            notification_sent_status[end_key] = False # Reset end notification for the new session

        # Check for session end
        elif session_end <= now < session_end + timedelta(minutes=1) and not notification_sent_status[end_key]:
            send_telegram_message(f"👋 *{session_name} Session Ended!* 👋\nTime: {session_end.strftime('%H:%M')} {TIMEZONE_STR}")
            notification_sent_status[end_key] = True
            notification_sent_status[start_key] = False # Reset start notification for the next day

        # If outside session times, reset flags for the next day
        elif now > session_end + timedelta(minutes=1) and notification_sent_status[start_key] and notification_sent_status[end_key]:
            # Both start and end notifications sent, and we are past the session.
            # This means we are ready to reset for the next day.
            notification_sent_status[start_key] = False
            notification_sent_status[end_key] = False
        elif now < session_start - timedelta(minutes=1) and notification_sent_status[start_key] and notification_sent_status[end_key]:
            # Before the session starts, and both flags are true (meaning they were set from a previous day)
            notification_sent_status[start_key] = False
            notification_sent_status[end_key] = False


def main():
    print("Starting session notifier...")
    # Schedule check_session_status to run every minute
    schedule.every(1).minute.do(check_session_status)

    # Initial check on startup
    check_session_status()

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
