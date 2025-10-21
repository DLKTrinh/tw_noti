from config import TELEGRAM_CHAT_ID
from .bot_handlers import bot

def send_telegram_message(message):
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        print(f"Sent to Telegram: {message}")
    except Exception as e:
        print(f"Error sending message to Telegram: {e}")