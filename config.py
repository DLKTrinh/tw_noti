from dotenv import load_dotenv
from threading import Lock
from dal.group_helpers import load_groups, GroupData
from dal.monitored_users import load_monitored_users
from typing import TypedDict
from datetime import datetime
from selenium.webdriver.remote.webdriver import WebDriver
import os
import telebot

load_dotenv(override=True)


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} is not set in your .env file")
    return value


# Retrieve tokens and paths from .env file
TELEGRAM_BOT_TOKEN: str = _require_env('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID: str = _require_env('TELEGRAM_CHAT_ID')
chrome_driver_path: str = _require_env('PATH_TO_CHROMEDRIVER')

# Cookie file written by setup_session.py, read by load_cookies() at startup
COOKIES_FILE: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'twitter_cookies.pkl')

# Set up the Telegram bot
bot: telebot.TeleBot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


class BotState(TypedDict):
    running: bool
    driver: WebDriver | None
    monitored_users: set[str]
    last_command_time: datetime | None
    group_data: GroupData
    fetch_failures: dict[str, int]


# Global state
bot_state: BotState = {
    'running': False,
    'driver': None,
    'monitored_users': set(),
    'last_command_time': None,
    'group_data': load_groups(),
    'fetch_failures': {},
}

bot_state['monitored_users'] = load_monitored_users()

driver_lock: Lock = Lock()