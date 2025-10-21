import os

def cleanup_temp_files():
    # Clean up our chrome_temp directory
    temp_dir = os.path.join(os.getcwd(), "chrome_temp")
    files_deleted = 0
    files_skipped = 0
    
    try:
        if os.path.exists(temp_dir):
            print(f"\nStarting cleanup in {temp_dir}")
            for root, dirs, files in os.walk(temp_dir, topdown=False):
                # Try to remove files
                for name in files:
                    try:
                        file_path = os.path.join(root, name)
                        os.remove(file_path)
                        files_deleted += 1
                    except (PermissionError, OSError):
                        files_skipped += 1
                        continue
                
                # Try to remove empty directories
                for name in dirs:
                    try:
                        dir_path = os.path.join(root, name)
                        os.rmdir(dir_path)
                    except (PermissionError, OSError):
                        continue

            print(f"\nChrome temp directory cleanup:")
            print(f"Files deleted: {files_deleted}")
            print(f"Files skipped: {files_skipped}")

        # Clean up Windows temp Chrome folders
        windows_temp = os.environ.get('TEMP', os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Temp'))
        chrome_temps = 0
        
        print("\nCleaning up Windows temp Chrome folders...")
        for item in os.listdir(windows_temp):
            if item.startswith(('chrome_BITS', 'scoped_dir')):
                try:
                    full_path = os.path.join(windows_temp, item)
                    if os.path.isdir(full_path):
                        import shutil
                        shutil.rmtree(full_path, ignore_errors=True)
                        chrome_temps += 1
                except Exception:
                    continue
        
        if chrome_temps > 0:
            print(f"Removed {chrome_temps} Chrome temporary folders from Windows temp")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")