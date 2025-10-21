import os
from .fetch_following_list import get_following_list
from dal.following_list import load_existing_following, save_to_csv
from dal.get_all import get_all_users_who_follow_target
from telegram_bot.telegram_bot import send_telegram_message
from dal.monitored_groups import get_group_users, get_user_groups
from config import bot_state

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
        return
            
    # Check if any new users in the sample
    new_following = set(sample_following) - existing_following
    
    if new_following:
        print(f"\nFound total of {len(new_following)} new following:")
        
        # Only send notification if this is not the first time monitoring this user
        if not is_new_user:
            # Create message with shared following information
            group_data = bot_state.get("group_data", {})
            user_groups = get_user_groups(group_data, username)
            print(f"[DEBUG] User '{username}' belongs to groups: {user_groups}")

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
                        print(f"[DEBUG] Group followers of '{followed_user}' within '{group_name}': {group_followers}")

                        if len(group_followers) >= 2:  # 2 or more other members followed
                            shared_message = (
                                f"📢 Group \"{group_name.title()}\": https://x.com/{followed_user} \n"
                                f"({', '.join(group_followers)})"
                            )

                            print(f"[DEBUG] Sending Telegram alert for '{followed_user}' in group '{group_name}'")
                            send_telegram_message(shared_message)
                            print(f"[INFO] Group '{group_name}' detected {len(group_followers)}+ follows for {followed_user}")
                        else:
                            print(f"[DEBUG] Not enough followers in '{group_name}' for '{followed_user}' (found {len(group_followers)})")

        else:
            print("First time monitoring this user - skipping notification")
        
        # Print to console for logging
        for i, user in enumerate(new_following, 1):
            print(f"{i}: {user}")
                
        # Append new followers to CSV
        save_to_csv(username, list(new_following), append=True)
    else:
        print("\nNo new following found in sample.")