import time
import json
from config import TELEGRAM_CHAT_ID, bot_state, bot
from utils.cleanup_temp import cleanup_temp_files
from utils.ensure_driver import ensure_valid_driver
from dal.monitored_users import load_monitored_users
from dal.monitored_groups import save_groups
from datetime import datetime

def save_monitored_users():
    with open('monitored_users.json', 'w') as f:
        json.dump(list(bot_state['monitored_users']), f)

# Command handlers
@bot.message_handler(commands=['start'])
def start_bot(message):
    print(f"\nReceived /start command at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n=== Debug Information ===")
    print(f"Message from chat ID: {message.chat.id}")
    print(f"Expected chat ID: {TELEGRAM_CHAT_ID}")
    print(f"Type of message.chat.id: {type(message.chat.id)}")
    print(f"Type of TELEGRAM_CHAT_ID: {type(TELEGRAM_CHAT_ID)}")
    print("========================\n")
    
    if message.chat.id != int(TELEGRAM_CHAT_ID):
        bot.reply_to(message, f"Unauthorized access. Your chat ID is: {message.chat.id}")
        return
    
    if not bot_state['running']:
        bot_state['running'] = True
        if not ensure_valid_driver():
            bot.reply_to(message, "Failed to start bot")
            bot_state['running'] = False
            bot_state['driver'] = None
            return
        bot.reply_to(message, "Bot started successfully! 🚀")
    else:
        bot.reply_to(message, "Bot is already running!")


@bot.message_handler(commands=['stop'])
def stop_bot(message):
    if message.chat.id != int(TELEGRAM_CHAT_ID):
        bot.reply_to(message, "Unauthorized access.")
        return
    
    if bot_state['running']:
        if bot_state['driver']:
            try:
                bot_state['driver'].quit()
            except:
                pass
        bot_state['running'] = False
        bot_state['driver'] = None
        cleanup_temp_files()
        bot.reply_to(message, "Bot stopped successfully! 🛑")
    else:
        bot.reply_to(message, "Bot is already stopped!")


@bot.message_handler(commands=['restart'])
def restart_bot(message):
    if message.chat.id != int(TELEGRAM_CHAT_ID):
        bot.reply_to(message, "Unauthorized access.")
        return
    
    stop_bot(message)
    time.sleep(2)
    start_bot(message)


@bot.message_handler(commands=['add'])
def add_user(message):
    if message.chat.id != int(TELEGRAM_CHAT_ID):
        bot.reply_to(message, "Unauthorized access.")
        return
    
    try:
        # Get all usernames after the command
        usernames = message.text.split()[1:]
        if usernames:
            added = []
            for username in usernames:
                username = username.strip()
                if username:
                    bot_state['monitored_users'].add(username)
                    added.append(username)
            
            if added:
                save_monitored_users()
                bot.reply_to(message, f"Added {len(added)} users: {', '.join(added)} ✅")
            else:
                bot.reply_to(message, "No valid usernames provided")
        else:
            bot.reply_to(message, "Please provide usernames: /add username1 username2 username3")
    except IndexError:
        bot.reply_to(message, "Please provide usernames: /add username1 username2 username3")


@bot.message_handler(commands=['remove'])
def remove_user(message):
    if message.chat.id != int(TELEGRAM_CHAT_ID):
        bot.reply_to(message, "Unauthorized access.")
        return
    
    try:
        # Get all usernames after the command
        usernames = message.text.split()[1:]
        if usernames:
            removed = []
            not_found = []
            for username in usernames:
                username = username.strip()
                if username:
                    if username in bot_state['monitored_users']:
                        bot_state['monitored_users'].remove(username)
                        removed.append(username)
                    else:
                        not_found.append(username)
            
            # Save changes if any users were removed
            if removed:
                save_monitored_users()
                
            # Prepare response message
            response = []
            if removed:
                response.append(f"Removed {len(removed)} users: {', '.join(removed)} ✅")
            if not_found:
                response.append(f"Users not found: {', '.join(not_found)}")
            
            bot.reply_to(message, "\n".join(response) if response else "No valid usernames provided")
        else:
            bot.reply_to(message, "Please provide usernames: /remove username1 username2 username3")
    except IndexError:
        bot.reply_to(message, "Please provide usernames: /remove username1 username2 username3")


@bot.message_handler(commands=['list'])
def list_users(message):
    if message.chat.id != int(TELEGRAM_CHAT_ID):
        bot.reply_to(message, "Unauthorized access.")
        return
    
    if bot_state['monitored_users']:
        users_list = "\n".join(bot_state['monitored_users'])
        bot.reply_to(message, f"Monitored users:\n{users_list}")
    else:
        bot.reply_to(message, "No users are being monitored.")


@bot.message_handler(commands=['creategr'])
def create_group(message):
    if message.chat.id != int(TELEGRAM_CHAT_ID):
        bot.reply_to(message, "Unauthorized access.")
        return
    try:
        group_name = message.text.split()[1]
        if group_name in bot_state['group_data']:
            bot.reply_to(message, f"Group '{group_name}' already exists.")
        else:
            bot_state['group_data'][group_name] = []
            save_groups(bot_state['group_data'])
            bot.reply_to(message, f"Group '{group_name}' created successfully ✅")
    except IndexError:
        bot.reply_to(message, "Usage: /creategr groupname")


@bot.message_handler(commands=['addtogr'])
def add_to_group(message):
    if message.chat.id != int(TELEGRAM_CHAT_ID):
        bot.reply_to(message, "Unauthorized access.")
        return
    try:
        _, group_name, *usernames = message.text.split()
        existing_users = load_monitored_users()

        if group_name not in bot_state['group_data']:
            bot.reply_to(message, f"Group '{group_name}' does not exist.")
            return

        group_users = set(bot_state['group_data'][group_name])
        added, not_found = [], []

        for username in usernames:
            if username not in existing_users:
                not_found.append(username)
            elif username not in group_users:
                group_users.add(username)
                added.append(username)

        bot_state['group_data'][group_name] = sorted(group_users)
        save_groups(bot_state['group_data'])

        response = []
        if added:
            response.append(f"✅ Added: {', '.join(added)}")
        if not_found:
            response.append(f"❌ Not found in monitored users: {', '.join(not_found)}")
        bot.reply_to(message, "\n".join(response) if response else "No users were added.")
    except Exception:
        bot.reply_to(message, "Usage: /addtogr groupname user1 user2 ...")


@bot.message_handler(commands=['removefromgr'])
def remove_from_group(message):
    if message.chat.id != int(TELEGRAM_CHAT_ID):
        bot.reply_to(message, "Unauthorized access.")
        return
    try:
        _, group_name, *usernames = message.text.split()

        if group_name not in bot_state['group_data']:
            bot.reply_to(message, f"Group '{group_name}' does not exist.")
            return

        group_users = set(bot_state['group_data'][group_name])
        removed = [u for u in usernames if u in group_users]
        group_users -= set(removed)

        bot_state['group_data'][group_name] = sorted(group_users)
        save_groups(bot_state['group_data'])

        if removed:
            bot.reply_to(message, f"✅ Removed: {', '.join(removed)}")
        else:
            bot.reply_to(message, "No matching users found in the group.")
    except Exception:
        bot.reply_to(message, "Usage: /removefromgr groupname user1 user2 ...")


@bot.message_handler(commands=['deletegr'])
def delete_group(message):
    if message.chat.id != int(TELEGRAM_CHAT_ID):
        bot.reply_to(message, "Unauthorized access.")
        return
    try:
        group_name = message.text.split()[1]
        if group_name in bot_state['group_data']:
            bot_state['group_data'].pop(group_name)
            save_groups(bot_state['group_data'])
            bot.reply_to(message, f"Group '{group_name}' deleted successfully 🗑️")
        else:
            bot.reply_to(message, f"Group '{group_name}' does not exist.")
    except IndexError:
        bot.reply_to(message, "Usage: /deletegr groupname")


@bot.message_handler(commands=['listgr'])
def list_groups(message):
    if message.chat.id != int(TELEGRAM_CHAT_ID):
        bot.reply_to(message, "Unauthorized access.")
        return
    groups = list(bot_state['group_data'].keys())
    if groups:
        bot.reply_to(message, "📁 Available groups:\n" + "\n".join(groups))
    else:
        bot.reply_to(message, "No groups found.")


@bot.message_handler(commands=['showgr'])
def show_group_users(message):
    if message.chat.id != int(TELEGRAM_CHAT_ID):
        bot.reply_to(message, "Unauthorized access.")
        return
    try:
        group_name = message.text.split()[1]
        users = bot_state['group_data'].get(group_name, [])
        if users:
            bot.reply_to(message, f"👥 Users in '{group_name}':\n" + "\n".join(users))
        else:
            bot.reply_to(message, f"Group '{group_name}' is empty or does not exist.")
    except IndexError:
        bot.reply_to(message, "Usage: /showgr groupname")


@bot.message_handler(commands=['help'])
def show_help(message):
    if message.chat.id != int(TELEGRAM_CHAT_ID):
        bot.reply_to(message, "Unauthorized access.")
        return
    
    help_text = """
Available commands:

/start - Start the bot
/stop - Stop the bot
/restart - Restart the bot
/add - Add users to monitor (/add user1 user2 user3 ...)
/remove - Remove a user from monitoring (/remove user1 user2 user3 ...)
/list - List all monitored users

        -------------------------------------------------------------

/creategr - Create a group (/create group1)
/addtogr - Add users to group (/addtogr group1 user1 user2 user3 ...)
/removefromgr - Remove users from a group (/removefromgr group1 user1 user2 user3)
/deletegr - Delete a group (/deletegr group1)
/listgr - List all groups
/showgr - Show all the users in a group (/showgr group1)
/help - Show this help message

Note: You can add or remove users while the bot is running!
The bot checks each monitored user every 5 minutes.
    """
    bot.reply_to(message, help_text)
