import time
import os
import json
from difflib import get_close_matches
from window_reader import get_active_window
from name_cleaner import clean_name
from obs_client import set_recording_directory, configure, get_recording_directory

CONFIG_FILE = "config.json"
GAME_MAP_FILE = "game_map.json"
POLL_INTERVAL = 2
FUZZY_MATCH_THRESHOLD = 0.75  # How similar a name needs to be (0.0 - 1.0)


def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_config(config: dict):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    print("[Setup] Config saved to config.json\n")


def first_time_setup():
    print("=" * 45)
    print("   OBS Game Organizer \u2014 First Time Setup")
    print("=" * 45)
    print("This will only run once. Your settings")
    print("will be saved for future launches.\n")

    name = input("What is your name or username? ").strip() or "User"
    host = input("OBS Host       (Enter = localhost): ").strip() or "localhost"
    port = input("OBS Port       (Enter = 4455):     ").strip() or "4455"
    password = input("OBS Password   (Enter = none):     ").strip()

    configure(host, int(port), password)

    print("\nConnecting to OBS to get your recording path...")
    obs_path = get_recording_directory()

    if obs_path:
        use_obs = input(f"\nOBS recording path found: {obs_path}\nUse this as base folder? (y/n): ").strip().lower()
        base_path = obs_path if use_obs == "y" else input("Enter your custom base recording path: ").strip()
    else:
        print("Could not reach OBS. You can set the path manually.")
        base_path = input("Enter your base recording path: ").strip()

    config = {
        "name": name,
        "obs_host": host,
        "obs_port": int(port),
        "obs_password": password,
        "base_recording_path": base_path
    }

    save_config(config)
    print(f"Welcome, {name}! Setup complete. Starting app...\n")
    return config


def returning_user_check(config: dict):
    name = config.get("name", "User")
    print("=" * 45)
    print(f"   Welcome back, {name}!")
    print("=" * 45)
    print(f"  OBS Host : {config['obs_host']}:{config['obs_port']}")
    print(f"  Save To  : {config['base_recording_path']}")
    print("=" * 45)
    answer = input(f"\nIs this still you, {name}? (y/n): ").strip().lower()

    if answer != "y":
        print("\nStarting fresh setup...\n")
        return first_time_setup()

    print(f"\nGreat! Starting OBS Game Organizer...\n")
    return config


def resolve_game_name(window_info: dict, game_map: dict) -> str:
    exe = window_info.get("exe", "").replace(".exe", "")
    title = window_info.get("title", "")

    for key, game_name in game_map.items():
        if key.lower() in exe.lower():
            return game_name

    for key, game_name in game_map.items():
        if key.lower() in title.lower():
            return game_name

    cleaned = clean_name(title)
    return cleaned if cleaned else "Unknown-Game"


def get_existing_folders(base_path: str) -> list:
    """Returns a list of existing folder names inside the base recording path."""
    if not os.path.exists(base_path):
        return []
    return [
        f for f in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, f))
    ]


def find_best_folder_match(game_name: str, existing_folders: list) -> str | None:
    """
    Looks through existing folders for a name close enough to game_name.
    Returns the matching folder name if found, or None if no match.

    Example:
      game_name = 'Fortnite-Chapter-5'
      existing  = ['Fortnite', 'Minecraft', 'Valorant']
      returns   -> 'Fortnite'  (close enough match)
    """
    if not existing_folders:
        return None

    matches = get_close_matches(
        game_name.lower(),
        [f.lower() for f in existing_folders],
        n=1,
        cutoff=FUZZY_MATCH_THRESHOLD
    )

    if matches:
        # Return the original folder name (not lowercased)
        matched_lower = matches[0]
        for folder in existing_folders:
            if folder.lower() == matched_lower:
                return folder

    return None


def resolve_folder_path(base_path: str, game_name: str) -> tuple[str, str]:
    """
    Finds the best folder for this game.
    - If a similar folder already exists, use that.
    - Otherwise create a new folder with the game name.
    Returns (folder_path, matched_or_created_name)
    """
    existing = get_existing_folders(base_path)
    match = find_best_folder_match(game_name, existing)

    if match:
        folder_path = os.path.join(base_path, match)
        print(f"[Folder] Matched '{game_name}' -> existing folder '{match}'")
        return folder_path, match
    else:
        folder_path = os.path.join(base_path, game_name)
        os.makedirs(folder_path, exist_ok=True)
        print(f"[Folder] Created new folder '{game_name}'")
        return folder_path, game_name


def main():
    # First time or returning user
    if not os.path.exists(CONFIG_FILE):
        config = first_time_setup()
    else:
        config = load_config()
        config = returning_user_check(config)

    configure(
        config["obs_host"],
        config["obs_port"],
        config["obs_password"]
    )

    BASE_RECORDING_PATH = config["base_recording_path"]

    with open(GAME_MAP_FILE, "r") as f:
        GAME_MAP = json.load(f)

    print("OBS Game Organizer is running...")
    print(f"Saving recordings to: {BASE_RECORDING_PATH}")
    print("Press Ctrl+C to stop.\n")

    last_game = None

    while True:
        window = get_active_window()
        game_name = resolve_game_name(window, GAME_MAP)

        if game_name != last_game:
            print(f"[Detected] {window.get('title', '')} -> {game_name}")
            folder_path, used_name = resolve_folder_path(BASE_RECORDING_PATH, game_name)
            set_recording_directory(folder_path)
            last_game = game_name

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
