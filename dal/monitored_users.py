import json

def load_monitored_users() -> set[str]:
    """Load monitored users from file."""
    try:
        with open('monitored_users.json', 'r') as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()