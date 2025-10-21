from dotenv import load_dotenv
from threading import Lock
from dal.group_helpers import load_groups
from dal.monitored_users import load_monitored_users
import os
import telebot

load_dotenv(override=True)

# Retrieve tokens and paths from .env file
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
chrome_driver_path = os.getenv('PATH_TO_CHROMEDRIVER')

# File to store cookies
COOKIES_FILE = 'twitter_cookies.pkl'

# Set up the Telegram bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Global state
bot_state = {
    'running': False,
    'driver': None,
    'monitored_users': set(),
    'last_command_time': None,  # Add this to track last command time
    'group_data': load_groups(),
}

bot_state['monitored_users'] = load_monitored_users()

driver_lock = Lock()