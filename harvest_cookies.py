import pickle
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from config import chrome_driver_path, COOKIES_FILE

USER_DATA_DIR = r"C:\Users\Acer\AppData\Local\Google\Chrome\User Data"
PROFILE_DIRECTORY = "Profile 2"


def harvest_cookies():
    service = Service(chrome_driver_path)
    options = Options()
    options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
    options.add_argument(f"--profile-directory={PROFILE_DIRECTORY}")
    # Headed, not headless - we just want to read existing login state.
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://x.com/home")
        time.sleep(3)

        if "login" in driver.current_url:
            print("This profile isn't logged into X. Log in normally in "
                  "your everyday Chrome first, then re-run this script.")
            return False

        cookies = driver.get_cookies()
        if not cookies:
            print("No cookies found on this profile for x.com.")
            return False

        with open(COOKIES_FILE, "wb") as f:
            pickle.dump(cookies, f)

        print(f"Saved {len(cookies)} cookies to {COOKIES_FILE}")
        print("Restart the bot so it picks up the refreshed session.")
        return True

    finally:
        driver.quit()


if __name__ == "__main__":
    harvest_cookies()