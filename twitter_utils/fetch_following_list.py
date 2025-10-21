import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def get_following_list(username, driver, n):
    url = f'https://twitter.com/{username}/following'

    try:
        driver.refresh()
        driver.get(url)
        time.sleep(5)  # Initial load wait

        following_set = set()
        processed_cells = set()
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0

        while len(following_set) < n:
            # Wait for cells to be present
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-testid="cellInnerDiv"]'))
            )

            user_cells = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="cellInnerDiv"]')
            for cell in user_cells:
                try:
                    cell_pos = driver.execute_script("return arguments[0].getBoundingClientRect();", cell)
                    cell_id = f"{cell_pos['top']}_{cell_pos['left']}"
                    
                    if cell_id not in processed_cells:
                        button = WebDriverWait(cell, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'button[data-testid="UserCell"]'))
                        )
                        spans = button.find_elements(By.TAG_NAME, 'span')
                        
                        for span in spans:
                            if span.text.startswith('@') and span.find_element(By.XPATH, './ancestor::a'):
                                following = span.text.replace('@', '')
                                if following not in following_set:
                                    following_set.add(following)
                                    processed_cells.add(cell_id)
                                    if len(following_set) >= n:
                                        return list(following_set)[:n]
                                break
                except Exception:
                    continue

            driver.execute_script("window.scrollBy(0, 350)")
            time.sleep(0.5)      

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                scroll_attempts += 1
                if scroll_attempts > 2:
                    print(f"Reached end of page. Found {len(following_set)} users.")
                    break
            else:
                scroll_attempts = 0
                last_height = new_height

    except Exception as e:
        print(f"Error while fetching the following list for {username}: {e}")

    print(f"Successfully found {len(following_set)} followers")
    return list(following_set)[:min(n, len(following_set))]
