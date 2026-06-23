import os
import shutil

# Subfolders inside the Chrome profile itself that are pure, regenerable
# cache - safe to wipe without touching login/session state. Cookies,
# Local Storage, IndexedDB, Login Data, etc. are deliberately NOT in this
# list and are never touched.
SAFE_TO_CLEAR_PROFILE_SUBFOLDERS: list[str] = [
    "Code Cache",
    "GPUCache",
]

# Subfolders at the User Data root (sibling to the profile, not inside it)
# that are also safe, regenerable cache/crash data.
SAFE_TO_CLEAR_USER_DATA_SUBFOLDERS: list[str] = [
    "Crashpad",
    "ShaderCache",
    "GrShaderCache",
]


def cleanup_profile_cache(chrome_profile_dir: str, chrome_profile_name: str) -> None:
    """
    Periodically clear ONLY regenerable Chrome cache folders inside the
    bot's persistent, logged-in profile - to stop disk usage growing
    forever. Deliberately does NOT touch Cookies, Local Storage,
    IndexedDB, Login Data, or anything tied to the logged-in session, so
    this can run on a schedule (or at shutdown) without ever logging the
    bot out.
    """
    profile_path = os.path.join(chrome_profile_dir, chrome_profile_name)
    cleared: list[tuple[str, int]] = []
    skipped: list[str] = []

    targets: list[tuple[str, str]] = (
        [(profile_path, name) for name in SAFE_TO_CLEAR_PROFILE_SUBFOLDERS] +
        [(chrome_profile_dir, name) for name in SAFE_TO_CLEAR_USER_DATA_SUBFOLDERS]
    )

    for base, name in targets:
        full_path = os.path.join(base, name)
        if os.path.exists(full_path):
            try:
                size_before = sum(
                    os.path.getsize(os.path.join(r, f))
                    for r, _, files in os.walk(full_path)
                    for f in files
                )
                shutil.rmtree(full_path, ignore_errors=True)
                cleared.append((full_path, size_before))
            except Exception:
                skipped.append(full_path)

    if cleared:
        total_mb = sum(size for _, size in cleared) / (1024 * 1024)
        print(f"\nCleared profile cache folders ({total_mb:.1f} MB freed):")
        for path, size in cleared:
            print(f"  - {path} ({size / (1024 * 1024):.1f} MB)")
    if skipped:
        print(f"Could not clear (likely locked by the running browser): {skipped}")


def cleanup_temp_files() -> None:
    # Clean up our chrome_temp directory (legacy - harmless no-op now that
    # the bot uses a persistent profile instead of a disposable one, kept
    # here in case anything still creates it)
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
                        shutil.rmtree(full_path, ignore_errors=True)
                        chrome_temps += 1
                except Exception:
                    continue
        
        if chrome_temps > 0:
            print(f"Removed {chrome_temps} Chrome temporary folders from Windows temp")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")