import os
import json

GROUPS_FILE = "groups.json"

def load_groups():
    if not os.path.exists(GROUPS_FILE):
        return {}

    with open(GROUPS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Ensure every group follows the new format
    fixed_data = {}
    for group_name, group_value in data.items():
        if isinstance(group_value, dict):  # already new format
            fixed_data[group_name] = group_value
        else:
            # old format -> convert
            fixed_data[group_name] = {
                "members": group_value,
                "threshold": 2  # default threshold
            }

    return fixed_data


def save_groups(groups_data):
    with open(GROUPS_FILE, "w", encoding="utf-8") as f:
        json.dump(groups_data, f, ensure_ascii=False, indent=2)

def get_user_groups(groups_data, username):
    user_groups = [
        group_name
        for group_name, group_info in groups_data.items()
        if username in group_info.get("members", [])
    ]
    return user_groups

def get_group_users(group_data, group_name):
    return group_data.get(group_name, {}).get("members", [])

def get_group_threshold(group_data, group_name):
    return group_data.get(group_name, {}).get("threshold", 3)

