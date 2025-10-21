import time
import threading
import sys
from telegram_bot.bot_handlers import bot
from config import bot_state
from datetime import datetime
from selenium.common.exceptions import WebDriverException
from utils.ensure_driver import ensure_valid_driver
from twitter_utils.monitor_following import monitor_following
from utils.cleanup_temp import cleanup_temp_files


def bot_polling():
    while True:
        try:
            print("Starting bot polling...")
            bot.polling(none_stop=True, timeout=60, long_polling_timeout=30)
        except Exception as e:
            print(f"Bot polling error: {e}")
            print("Restarting bot polling in 5 seconds...")
            time.sleep(5)

def main():
    
    # Configure bot polling with longer timeout and retry
    bot.threaded = True
    bot.skip_pending = True
    
    # Start the bot polling in a separate thread with error handling
    bot_thread = threading.Thread(target=bot_polling, daemon=True)
    bot_thread.start()
    
    check_interval = 300  # 5 minutes in seconds
    cleanup_counter = 0  # Counter to track number of checks

    try:
        while True:
            if bot_state['running']:
                try:
                    print(f"\nStarting check at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # Ensure we have a valid driver before starting checks
                    if not ensure_valid_driver():
                        print("Failed to initialize driver, waiting 60 seconds before retry...")
                        time.sleep(60)
                        continue

                    for username in bot_state['monitored_users']:
                        try:
                            print(f"\nMonitoring user: {username}")
                            monitor_following(username, bot_state['driver'])
                        except WebDriverException as e:
                            print(f"WebDriver error for {username}: {e}")
                            # Force driver reinitialization on next iteration
                            bot_state['driver'] = None
                            continue
                        except Exception as e:
                            print(f"Error monitoring {username}: {e}")
                            continue

                    cleanup_counter += 1
                    if cleanup_counter >= 12:  # After 12 checks (1 hour)
                        print("\nCleaning up temporary files...")
                        cleanup_temp_files()
                        cleanup_counter = 0  # Reset counter

                    time.sleep(check_interval)

                except Exception as e:
                    print(f"Error in main loop: {e}")
                    if bot_state['driver']:
                        try:
                            bot_state['driver'].quit()
                        except:
                            pass
                        bot_state['driver'] = None
                    print("Waiting 60 seconds before retrying...")
                    time.sleep(60)
            else:
                time.sleep(1)  # Sleep briefly when bot is not running

    except KeyboardInterrupt:
        print("\nReceived Ctrl+C. Shutting down gracefully...")
        if bot_state['driver']:
            try:
                print("Closing Chrome browser...")
                bot_state['driver'].quit()
                time.sleep(2)
            except Exception as e:
                print(f"Error closing Chrome browser: {e}")
            bot_state['driver'] = None

        try:
            print("Cleaning up temporary files...")
            cleanup_temp_files()
            print("Temporary files cleaned up")
        except Exception as e:
            print(f"Error during final cleanup: {e}")

        print("Shutdown complete!")
        sys.exit(0)

if __name__ == "__main__":
    main()


            