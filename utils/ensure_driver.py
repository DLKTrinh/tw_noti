from config import bot_state, driver_lock, COOKIES_FILE
from .selenium_driver import setup_driver
from .load_cookie import load_cookies


def ensure_valid_driver() -> bool:
    """Ensure we have a valid driver, reinitialize if needed."""
    with driver_lock:
        if bot_state['driver'] is None:
            print("Driver is None, reinitializing...")
            driver = setup_driver()
            if not load_cookies(driver, COOKIES_FILE):
                print("Failed to load cookies. Run setup_session.py to "
                      "refresh the session, then restart the bot.")
                driver.quit()
                return False

            bot_state['driver'] = driver
            print("Driver initialized successfully.")

        return True