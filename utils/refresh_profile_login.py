"""

Run this if the bot's dedicated Chrome profile (chrome_profile_copy) ever
gets logged out - session expiry, X forcing a re-auth, etc. Opens that
profile in a VISIBLE window so you can log back in by hand. Never touches
your daily Chrome profile.

IMPORTANT: stop the bot before running this - it holds the same profile
folder open while running, and Chrome won't let two processes share it.

Usage:
    python refresh_profile_login.py
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from config import chrome_driver_path, chrome_profile_dir, chrome_profile_name


def refresh_login():
    service = Service(chrome_driver_path)
    options = Options()
    options.add_argument(f"--user-data-dir={chrome_profile_dir}")
    options.add_argument(f"--profile-directory={chrome_profile_name}")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://x.com/login")
        print("\nLog in to X in the window that just opened.")
        input("Once logged in and you can see your home timeline, press Enter here...")
        print("Session refreshed. You can restart the bot now.")
    finally:
        driver.quit()


if __name__ == "__main__":
    refresh_login()
