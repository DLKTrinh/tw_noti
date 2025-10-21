import os
import csv

def save_to_csv(username, following_list, append=False):
    # Create user directory if it doesn't exist
    user_dir = os.path.join(os.getcwd(), "users")
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    
    filename = os.path.join(user_dir, f"{username}_following.csv")
    
    # Check if file exists
    file_exists = os.path.exists(filename)
    
    # If appending but file doesn't exist, we need to write header first
    mode = 'a' if (append and file_exists) else 'w'
    
    with open(filename, mode, newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:  # Write header for new files
            writer.writerow(['Username'])  # Header
        for following in following_list:
            writer.writerow([following])
    
    print(f"Data {'appended to' if append else 'saved to'} {filename}")
    return filename


def load_existing_following(filename):
    # Ensure we're looking in the user directory
    user_dir = os.path.join(os.getcwd(), "users")
    full_path = os.path.join(user_dir, os.path.basename(filename))
    
    existing_following = set()
    try:
        with open(full_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                existing_following.add(row[0])
    except FileNotFoundError:
        pass  # File doesn't exist yet, that's okay
    return existing_following
