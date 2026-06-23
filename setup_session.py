"""
setup_session.py

One-off setup script. Run this manually whenever you need to refresh the
bot's session (first-time setup, or after X logs the session out).

What it does:
  1. Copies your real Chrome profile into chrome_profile_copy/ (isolated
     from your daily browser so the bot never touches your real profile).
  2. Opens the copy briefly to extract the X/Twitter session cookies.
  3. Saves them to twitter_cookies.pkl which the bot reads at startup.

Usage:
    py setup_session.py

Requirements:
  - Close Chrome completely before running (check Task Manager for
    lingering chrome.exe processes).
  - Your real Chrome profile must already be logged into X/Twitter.
"""

import os
import pickle
import shutil
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

load_dotenv(override=True)

# --- Config ---
# Your REAL Chrome profile (source). Get from chrome://version -> Profile Path.
# Split into parent dir and last folder name:
REAL_PROFILE_DIR: str = os.getenv(
    'CHROME_PROFILE_DIR',
    r"C:\Users\acer\AppData\Local\Google\Chrome\User Data"
)
REAL_PROFILE_NAME: str = os.getenv('CHROME_PROFILE_NAME', 'Profile 2')

# Where the isolated copy lives (inside your project root)
PROJECT_ROOT: str = os.path.dirname(os.path.abspath(__file__))
COPY_DIR: str = os.path.join(PROJECT_ROOT, "chrome_profile_copy")
COOKIES_FILE: str = os.path.join(PROJECT_ROOT, "twitter_cookies.pkl")
CHROME_DRIVER_PATH: str = os.getenv('PATH_TO_CHROMEDRIVER', '')


def copy_profile() -> str:
    """Copy the real profile into the project. Returns the copy path."""
    src = os.path.join(REAL_PROFILE_DIR, REAL_PROFILE_NAME)
    dst = os.path.join(COPY_DIR, REAL_PROFILE_NAME)

    if not os.path.isdir(src):
        raise RuntimeError(
            f"Source profile not found: {src}\n"
            "Check CHROME_PROFILE_DIR and CHROME_PROFILE_NAME in your .env "
            "match what chrome://version shows under 'Profile Path'."
        )

    print(f"Copying profile from:\n  {src}\nto:\n  {dst}")
    print("This may take a moment depending on profile size...")

    if os.path.exists(dst):
        shutil.rmtree(dst)

    shutil.copytree(src, dst)
    print(f"Profile copied successfully.")
    return dst


def extract_cookies() -> bool:
    """Open the profile copy, extract X cookies, save to pickle."""
    if not CHROME_DRIVER_PATH:
        raise RuntimeError("PATH_TO_CHROMEDRIVER is not set in your .env file.")

    service = Service(CHROME_DRIVER_PATH)
    options = Options()
    options.add_argument(f"--user-data-dir={COPY_DIR}")
    options.add_argument(f"--profile-directory={REAL_PROFILE_NAME}")
    options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--log-level=3")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    print("\nOpening profile copy to extract cookies...")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://x.com/home")
        time.sleep(3)

        if "login" in driver.current_url:
            print(
                "\nThe profile copy is not logged into X.\n"
                "Make sure your real Chrome profile is logged in first,\n"
                "then re-run this script."
            )
            return False

        cookies = driver.get_cookies()
        if not cookies:
            print("No cookies found.")
            return False

        with open(COOKIES_FILE, "wb") as f:
            pickle.dump(cookies, f)

        print(f"Saved {len(cookies)} cookies to {COOKIES_FILE}")
        return True

    finally:
        driver.quit()


def main() -> None:
    print("=== Bot Session Setup ===\n")

    # Step 1: copy profile
    try:
        copy_profile()
    except RuntimeError as e:
        print(f"Error: {e}")
        return

    # Step 2: extract cookies
    success = extract_cookies()
    if not success:
        return

    print(
        "\nSetup complete. You can now start the bot.\n"
        "Re-run this script whenever X logs the session out."
    )


if __name__ == "__main__":
    main()
