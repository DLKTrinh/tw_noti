import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Hard safety valves - the loop can NEVER hang forever, no matter what
# weirdness the page throws at us.
MAX_SCROLL_ITERATIONS = 60
MAX_DURATION_SECONDS = 90


def get_following_list(username, driver, n):
    url = f'https://twitter.com/{username}/following'
    following_set = set()

    try:
        driver.refresh()
        driver.get(url)
        time.sleep(5)  # Initial load wait

        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        loop_count = 0
        start_time = time.time()

        while len(following_set) < n:
            loop_count += 1
            elapsed = time.time() - start_time

            # --- Hard cap: bail out no matter what, so we can never freeze the bot ---
            if loop_count > MAX_SCROLL_ITERATIONS or elapsed > MAX_DURATION_SECONDS:
                print(f"[{username}] Bailing out after {loop_count} scrolls / "
                      f"{elapsed:.0f}s with {len(following_set)} users found "
                      f"(target was {n}).")
                break

            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, 'div[data-testid="cellInnerDiv"]')
                    )
                )
            except Exception:
                print(f"[{username}] Timed out waiting for cells on scroll {loop_count}.")
                break

            user_cells = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="cellInnerDiv"]')
            found_this_pass = 0

            for cell in user_cells:
                try:
                    button = cell.find_element(By.CSS_SELECTOR, 'button[data-testid="UserCell"]')
                    spans = button.find_elements(By.TAG_NAME, 'span')

                    for span in spans:
                        text = span.text
                        if text.startswith('@'):
                            handle = text[1:]
                            # Dedup by the actual handle, NOT by on-screen position.
                            # The list is virtualized, so positions get recycled
                            # for different users as you scroll - position-based
                            # dedup silently drops real new users.
                            if handle not in following_set:
                                following_set.add(handle)
                                found_this_pass += 1
                                if len(following_set) >= n:
                                    print(f"[{username}] Reached target of {n} users.")
                                    return list(following_set)[:n]
                            break
                except Exception:
                    continue

            print(f"[{username}] Scroll {loop_count}: {len(following_set)} unique users "
                  f"so far (+{found_this_pass} this pass).")

            # One-time diagnostic: if the very first pass found cellInnerDiv
            # elements but extracted zero real users from them, dump what's
            # actually on the page so we can see why (protected account,
            # rate-limit interstitial, X changed their markup, etc).
            if loop_count == 1 and found_this_pass == 0 and len(user_cells) > 0:
                try:
                    diag_dir = "diagnostics"
                    import os
                    os.makedirs(diag_dir, exist_ok=True)
                    print(f"[{username}] DIAGNOSTIC - page title: {driver.title!r}, "
                          f"url: {driver.current_url}, cellInnerDiv count: {len(user_cells)}")
                    shot_path = os.path.join(diag_dir, f"{username}_empty_following.png")
                    driver.save_screenshot(shot_path)
                    print(f"[{username}] DIAGNOSTIC - screenshot saved to {shot_path}")
                except Exception as diag_err:
                    print(f"[{username}] DIAGNOSTIC capture failed: {diag_err}")

            driver.execute_script("window.scrollBy(0, 350)")
            time.sleep(0.5)

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                scroll_attempts += 1
                if scroll_attempts > 2:
                    print(f"[{username}] Reached end of page. Found {len(following_set)} users.")
                    break
            else:
                scroll_attempts = 0
                last_height = new_height

    except Exception as e:
        print(f"Error while fetching the following list for {username}: {e}")

    print(f"[{username}] Successfully found {len(following_set)} users.")
    return list(following_set)[:min(n, len(following_set))]