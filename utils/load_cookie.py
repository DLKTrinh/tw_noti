import time
import pickle

def load_cookies(driver, file_path):
    try:
        driver.get('https://twitter.com')
        time.sleep(2)

        with open(file_path, 'rb') as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)

        driver.refresh()

        if "login" in driver.current_url:
            message = "Cookies are expired. Please log in manually to refresh them."
            print(message)
            return False
        else:
            print("Session loaded successfully from cookies.")
            return True
    
    except Exception as e:
        print(f"Error loading cookies: {e}")
        return False




