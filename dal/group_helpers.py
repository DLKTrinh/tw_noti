import os
import json
from typing import Any

GROUPS_FILE = "groups.json"

# A group looks like: {"members": ["alice", "bob"], "threshold": 2}
GroupInfo = dict[str, Any]
GroupData = dict[str, GroupInfo]


def load_groups() -> GroupData:
    if not os.path.exists(GROUPS_FILE):
        return {}

    with open(GROUPS_FILE, "r", encoding="utf-8") as f:
        data: GroupData = json.load(f)

    # Ensure every group follows the new format
    fixed_data: GroupData = {}
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


def save_groups(groups_data: GroupData) -> None:
    with open(GROUPS_FILE, "w", encoding="utf-8") as f:
        json.dump(groups_data, f, ensure_ascii=False, indent=2)


def get_user_groups(groups_data: GroupData, username: str) -> list[str]:
    user_groups = [
        group_name
        for group_name, group_info in groups_data.items()
        if username in group_info.get("members", [])
    ]
    return user_groups


def get_group_users(group_data: GroupData, group_name: str) -> list[str]:
    return group_data.get(group_name, {}).get("members", [])


def get_group_threshold(group_data: GroupData, group_name: str) -> int:
    return group_data.get(group_name, {}).get("threshold", 3)