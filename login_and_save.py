"""
login_and_save.py

Copies your real Chrome profile to a non-default location (required by
ChromeDriver), opens it in a visible window so you can confirm you're
logged into X/Twitter, then saves the session cookies to twitter_cookies.pkl.

Run this whenever the bot's session expires.

Usage:
    1. Close Chrome completely first
    2. py login_and_save.py

.env variables used:
    PATH_TO_CHROMEDRIVER      - path to chromedriver.exe
    CHROME_PROFILE_DIR        - your real Chrome User Data folder
    CHROME_PROFILE_NAME       - profile folder name (e.g. Profile 2)
    CHROME_PROFILE_COPY_DIR   - where to put the copy (e.g. D:\\TeleBot\\Tw_Noti\\chrome_profile_copy)
"""

import os
import sys
import pickle
import shutil
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

load_dotenv(override=True)

CHROME_DRIVER_PATH: str = os.getenv('PATH_TO_CHROMEDRIVER', '')
CHROME_PROFILE_DIR: str = os.getenv('CHROME_PROFILE_DIR', '')
CHROME_PROFILE_NAME: str = os.getenv('CHROME_PROFILE_NAME', 'Profile 2')
CHROME_PROFILE_COPY_DIR: str = os.getenv('CHROME_PROFILE_COPY_DIR', '')
COOKIES_FILE: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'twitter_cookies.pkl')


def copy_profile() -> None:
    src = os.path.join(CHROME_PROFILE_DIR, CHROME_PROFILE_NAME)
    dst = os.path.join(CHROME_PROFILE_COPY_DIR, CHROME_PROFILE_NAME)

    if not os.path.isdir(src):
        raise RuntimeError(f"Source profile not found: {src}")

    print(f"Copying profile to {dst} ...")
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    print("Profile copied.")


def main() -> None:
    if not CHROME_DRIVER_PATH:
        raise RuntimeError("PATH_TO_CHROMEDRIVER is not set in your .env")
    if not CHROME_PROFILE_DIR:
        raise RuntimeError("CHROME_PROFILE_DIR is not set in your .env")
    if not CHROME_PROFILE_COPY_DIR:
        raise RuntimeError("CHROME_PROFILE_COPY_DIR is not set in your .env")

    copy_profile()

    service = Service(CHROME_DRIVER_PATH)
    options = Options()
    # Point at the COPY, not the real profile - ChromeDriver rejects the
    # default Chrome User Data dir with a remote debugging error.
    options.add_argument(f"--user-data-dir={CHROME_PROFILE_COPY_DIR}")
    options.add_argument(f"--profile-directory={CHROME_PROFILE_NAME}")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--log-level=3")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-session-crashed-bubble")
    options.add_argument("--disable-infobars")
    options.add_argument("--hide-crash-restore-bubble")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("about:blank")
        time.sleep(1)
        driver.get("https://x.com/home")
        time.sleep(3)

        print("\nLog in to X if needed.", flush=True)
        print("When you're ready to save cookies, come back here and press Enter...", flush=True)
        sys.stdin.readline()

        cookies = driver.get_cookies()
        if not cookies:
            print("No cookies found - something went wrong.", flush=True)
            return

        with open(COOKIES_FILE, "wb") as f:
            pickle.dump(cookies, f)

        print(f"Saved {len(cookies)} cookies to {COOKIES_FILE}", flush=True)
        print("You can now start the bot.", flush=True)

    finally:
        driver.quit()


if __name__ == "__main__":
    main()