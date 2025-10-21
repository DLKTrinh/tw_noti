from config import bot_state
from .following_list import load_existing_following

def get_all_users_who_follow_target(target_user):
    users_who_follow_target = []

    # Use the in-memory list of monitored users
    monitored_users = bot_state.get('monitored_users', set())

    for username in monitored_users:
        csv_file = f"{username}_following.csv"
        following_list = load_existing_following(csv_file)

        if target_user in following_list:
            users_who_follow_target.append(username)

    return users_who_follow_target
