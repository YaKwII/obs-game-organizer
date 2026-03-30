import time
import os
import json
from window_reader import get_active_window
from name_cleaner import clean_name
from obs_client import set_recording_directory

# --- SETTINGS ---
BASE_RECORDING_PATH = r"C:\Users\YourName\Videos\OBS-Recordings"  # Change this!
POLL_INTERVAL = 2  # How often to check the active window (seconds)
GAME_MAP_FILE = "game_map.json"

# Load custom game mappings
with open(GAME_MAP_FILE, "r") as f:
    GAME_MAP = json.load(f)


def resolve_game_name(window_info: dict) -> str:
    """
    Tries to match the window title or exe to a known game.
    Falls back to the cleaned window title if no match found.
    """
    exe = window_info.get("exe", "").replace(".exe", "")
    title = window_info.get("title", "")

    # Check exe against game map first (more reliable)
    for key, game_name in GAME_MAP.items():
        if key.lower() in exe.lower():
            return game_name

    # Then check title
    for key, game_name in GAME_MAP.items():
        if key.lower() in title.lower():
            return game_name

    # Fallback: clean the raw title
    cleaned = clean_name(title)
    return cleaned if cleaned else "Unknown-Game"


def ensure_folder(path: str):
    os.makedirs(path, exist_ok=True)


def main():
    print("OBS Game Organizer running...")
    print(f"Base path: {BASE_RECORDING_PATH}")
    print("Press Ctrl+C to stop.\n")

    last_game = None

    while True:
        window = get_active_window()
        game_name = resolve_game_name(window)
        folder_path = os.path.join(BASE_RECORDING_PATH, game_name)

        if game_name != last_game:
            print(f"[Detected] {window.get('title', '')} -> Game: {game_name}")
            ensure_folder(folder_path)
            set_recording_directory(folder_path)
            last_game = game_name

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
