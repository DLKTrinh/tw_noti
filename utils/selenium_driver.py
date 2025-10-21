from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from config import chrome_driver_path
import os

def setup_driver():
    service = Service(chrome_driver_path)
    options = Options()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # Add headless mode
    options.add_argument("--headless=new")
    
    # Add cleanup and performance options
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Disable logging
    options.add_argument("--log-level=3")  # Fatal errors only

    # Suppress Chrome WebGL fallback warning
    options.add_argument("--enable-unsafe-swiftshader")
    
    # Set up cache handling properly
    options.add_argument("--aggressive-cache-discard")
    options.add_argument("--disable-cache")
    options.add_argument("--disable-application-cache")
    options.add_argument("--disable-offline-load-stale-cache")
    options.add_argument("--disk-cache-size=0")
    
    # Set specific temp directory
    temp_dir = os.path.join(os.getcwd(), "chrome_temp")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    options.add_argument(f"--user-data-dir={temp_dir}")
    
    return webdriver.Chrome(service=service, options=options)
