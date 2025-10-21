from config import COOKIES_FILE, bot_state, driver_lock
from .selenium_driver import setup_driver
from .load_cookie import load_cookies

def ensure_valid_driver():
    """Ensure we have a valid driver, reinitialize if needed"""
    with driver_lock:
        if bot_state['driver'] is None:
            print("Driver is None, reinitializing...")
            bot_state['driver'] = setup_driver()
            if not load_cookies(bot_state['driver'], COOKIES_FILE):
                print("Failed to reinitialize driver: Invalid cookies")
                return False
        return True
