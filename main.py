import time
import os
import json
from window_reader import get_active_window
from name_cleaner import clean_name
from obs_client import set_recording_directory, configure, get_recording_directory

CONFIG_FILE = "config.json"
GAME_MAP_FILE = "game_map.json"
POLL_INTERVAL = 2


def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_config(config: dict):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    print("[Setup] Config saved to config.json\n")


def first_time_setup():
    print("=" * 45)
    print("   OBS Game Organizer — First Time Setup")
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


def ensure_folder(path: str):
    os.makedirs(path, exist_ok=True)


def main():
    # First time or returning user
    if not os.path.exists(CONFIG_FILE):
        config = first_time_setup()
    else:
        config = load_config()
        config = returning_user_check(config)

    # Apply OBS connection settings from config
    configure(
        config["obs_host"],
        config["obs_port"],
        config["obs_password"]
    )

    BASE_RECORDING_PATH = config["base_recording_path"]

    # Load game map
    with open(GAME_MAP_FILE, "r") as f:
        GAME_MAP = json.load(f)

    print("OBS Game Organizer is running...")
    print(f"Saving recordings to: {BASE_RECORDING_PATH}")
    print("Press Ctrl+C to stop.\n")

    last_game = None

    while True:
        window = get_active_window()
        game_name = resolve_game_name(window, GAME_MAP)
        folder_path = os.path.join(BASE_RECORDING_PATH, game_name)

        if game_name != last_game:
            print(f"[Detected] {window.get('title', '')} -> {game_name}")
            ensure_folder(folder_path)
            set_recording_directory(folder_path)
            last_game = game_name

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
