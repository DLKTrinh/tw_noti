import json

# Load monitored users from file
def load_monitored_users():
    try:
        with open('monitored_users.json', 'r') as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()