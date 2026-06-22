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

chrome_profile_dir = os.getenv(
    'CHROME_PROFILE_DIR',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chrome_profile_copy')
)
chrome_profile_name = os.getenv('CHROME_PROFILE_NAME', 'Profile 1')

# Set up the Telegram bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Global state
bot_state = {
    'running': False,
    'driver': None,
    'monitored_users': set(),
    'last_command_time': None,  # Add this to track last command time
    'group_data': load_groups(),
    'fetch_failures': {},  # username -> consecutive failed-fetch count
}

bot_state['monitored_users'] = load_monitored_users()

driver_lock = Lock()