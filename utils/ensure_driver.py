from config import bot_state, driver_lock
from .selenium_driver import setup_driver


def ensure_valid_driver():
    """Ensure we have a valid driver, reinitialize if needed."""
    with driver_lock:
        if bot_state['driver'] is None:
            print("Driver is None, reinitializing...")
            driver = setup_driver()

            # The profile already carries a logged-in session - no cookie
            # injection needed. Just confirm it's actually still active.
            driver.get("https://x.com/home")
            if "login" in driver.current_url:
                print("Driver init failed: the bot's Chrome profile is "
                      "not logged in to X. Run refresh_profile_login.py "
                      "to log back in, then restart the bot.")
                driver.quit()
                return False

            bot_state['driver'] = driver
            print("Driver initialized using the dedicated logged-in profile.")

        return True