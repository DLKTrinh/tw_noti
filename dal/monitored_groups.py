import os
import json

GROUPS_FILE = "groups.json"

def load_groups():
    if not os.path.exists(GROUPS_FILE):
        return {}
    with open(GROUPS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_groups(groups_data):
    with open(GROUPS_FILE, "w", encoding="utf-8") as f:
        json.dump(groups_data, f, ensure_ascii=False, indent=2)

def get_user_groups(groups_data, username):
    user_groups = [group for group, members in groups_data.items() if username in members]
    return user_groups

def get_group_users(groups_data, group_name):
    return groups_data.get(group_name, [])
