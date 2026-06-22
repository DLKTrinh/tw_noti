import os
from .fetch_following_list import get_following_list
from dal.following_list import load_existing_following, save_to_csv
from dal.get_all import get_all_users_who_follow_target
from telegram_bot.telegram_bot import send_telegram_message
from dal.group_helpers import get_group_users, get_user_groups, get_group_threshold
from config import bot_state

# How many consecutive failed fetches for the same user before we alert
# instead of failing silently every cycle.
FAILURE_ALERT_THRESHOLD = 3


def monitor_following(username, driver):
    csv_file = f"{username}_following.csv"
    user_dir = os.path.join(os.getcwd(), "users")
    full_path = os.path.join(user_dir, csv_file)
    
    # Check if this is first time monitoring this user 
    is_new_user = not os.path.exists(full_path)
    
    existing_following = load_existing_following(csv_file)
    
    # First check: Get small sample (5 users)
    print("\nChecking for new following...")
    sample_following = get_following_list(username, driver, 40)
    if not sample_following:  # If we couldn't get any users, skip this round
        print("Could not fetch sample following list. Skipping this check.")

        failures = bot_state.setdefault('fetch_failures', {})
        failures[username] = failures.get(username, 0) + 1
        count = failures[username]

        if count == FAILURE_ALERT_THRESHOLD:
            send_telegram_message(
                f"⚠️ Could not fetch the following list for {username} "
                f"{count} times in a row. It may be protected, suspended, "
                f"renamed, or X may have changed their page layout - "
                f"worth checking manually."
            )
        elif count > FAILURE_ALERT_THRESHOLD and count % 12 == 0:
            # Roughly once an hour at the default 5-minute check interval,
            # remind again so it doesn't get lost in the noise - but not
            # every single cycle.
            send_telegram_message(
                f"⚠️ Still failing to fetch the following list for "
                f"{username} ({count} consecutive failures)."
            )
        return

    # Fetch succeeded - clear any failure streak for this user
    bot_state.setdefault('fetch_failures', {})[username] = 0
            
    # Check if any new users in the sample
    new_following = set(sample_following) - existing_following
    
    if new_following:
        print(f"\nFound total of {len(new_following)} new following:")
        
        # Only send notification if this is not the first time monitoring this user
        if not is_new_user:
            # Create message with shared following information
            group_data = bot_state.get("group_data", {})
            user_groups = get_user_groups(group_data, username)

            if not user_groups:
                new_users_messages = []
                for followed_user in new_following:
                    # Get all users who follow this person
                    following_users = get_all_users_who_follow_target (followed_user)

                    # Always include current username first, then add others if they exist
                    other_users = [u for u in following_users if u != username]
                    users_str = f"({username}" + (f", {', '.join(other_users)}" if other_users else "") + ")"
                    new_users_messages.append(f"{username} : https://x.com/{followed_user} {users_str}")

                new_users_list = "\n".join(new_users_messages)
                message = f"🔔 {username} {len(new_following)} new account{'s' if len(new_following) > 1 else ''}:\n{new_users_list}"
                # Send a single consolidated message
                send_telegram_message(message)


            else:
                for group_name in user_groups:
                    group_members = get_group_users(group_data, group_name)
                    for followed_user in new_following:
                        # Get all monitored users who follow this same account
                        followers_of_target = get_all_users_who_follow_target(followed_user)

                        if username not in followers_of_target:
                            followers_of_target.append(username)

                        # Count how many are in this group
                        group_followers = [u for u in followers_of_target if u in group_members]

                        threshold = get_group_threshold(group_data, group_name)
                        if len(group_followers) >= threshold:  
                            shared_message = (
                                f"📢 Group \"{group_name.title()}\": https://x.com/{followed_user} \n"
                                f"({', '.join(group_followers)})"
                            )
                            print(f"Sending Telegram alert for '{followed_user}' in group '{group_name}'")
                            send_telegram_message(shared_message)
        else:
            print("First time monitoring this user - skipping notification")
        
        # Print to console for logging
        for i, user in enumerate(new_following, 1):
            print(f"{i}: {user}")
                
        # Append new followers to CSV
        save_to_csv(username, list(new_following), append=True)
    else:
        print("\nNo new following found in sample.")