# OBS WebSocket client
# Requires OBS 28+ with WebSocket server enabled
# Tools > WebSocket Server Settings > Enable WebSocket Server

import obsws_python as obs
import os
import shutil
from datetime import datetime

# These are set at runtime via configure()
_HOST = "localhost"
_PORT = 4455
_PASSWORD = ""

# Tracks the current game folder so we know where to move files
_CURRENT_GAME_FOLDER = ""
_CURRENT_GAME_NAME = ""


def configure(host: str, port: int, password: str):
    """Set OBS connection details from config."""
    global _HOST, _PORT, _PASSWORD
    _HOST = host
    _PORT = port
    _PASSWORD = password


def set_current_game(folder_path: str, game_name: str):
    """Called by main.py to track which game is currently active."""
    global _CURRENT_GAME_FOLDER, _CURRENT_GAME_NAME
    _CURRENT_GAME_FOLDER = folder_path
    _CURRENT_GAME_NAME = game_name


def get_recording_directory() -> str:
    """
    Reads the current recording path from OBS.
    Returns the path string or None if unreachable.
    """
    try:
        with obs.ReqClient(host=_HOST, port=_PORT, password=_PASSWORD) as client:
            response = client.get_profile_parameter("SimpleOutput", "FilePath")
            path = response.parameter_value
            print(f"[OBS] Recording path found: {path}")
            return path
    except Exception as e:
        print(f"[OBS] Could not read recording path: {e}")
        return None


def set_recording_directory(path: str):
    """
    Tells OBS to save recordings to the given directory path.
    """
    try:
        with obs.ReqClient(host=_HOST, port=_PORT, password=_PASSWORD) as client:
            client.set_profile_parameter("SimpleOutput", "FilePath", path)
            print(f"[OBS] Recording directory set to: {path}")
    except Exception as e:
        print(f"[OBS] Connection error: {e}")
        print("Make sure OBS is open and WebSocket is enabled.")


def get_latest_recording(folder: str) -> str | None:
    """
    Finds the most recently modified video file in a folder.
    Looks for common OBS output formats.
    """
    extensions = [".mp4", ".mkv", ".mov", ".flv", ".ts"]
    try:
        files = [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if os.path.splitext(f)[1].lower() in extensions
        ]
        if not files:
            return None
        return max(files, key=os.path.getmtime)
    except Exception:
        return None


def on_recording_stopped(base_path: str):
    """
    Called when OBS stops recording.
    Finds the latest recording file, renames it to include the game name
    and a timestamp, then moves it into the correct game folder.
    """
    if not _CURRENT_GAME_FOLDER or not _CURRENT_GAME_NAME:
        print("[OBS] Recording stopped but no game was tracked.")
        return

    print(f"[OBS] Recording stopped. Looking for file in: {_CURRENT_GAME_FOLDER}")
    latest = get_latest_recording(_CURRENT_GAME_FOLDER)

    if not latest:
        # Also check base path in case OBS saved it there
        latest = get_latest_recording(base_path)

    if not latest:
        print("[OBS] Could not find the recording file.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    ext = os.path.splitext(latest)[1]
    new_name = f"{_CURRENT_GAME_NAME}_{timestamp}{ext}"
    new_path = os.path.join(_CURRENT_GAME_FOLDER, new_name)

    try:
        shutil.move(latest, new_path)
        print(f"[OBS] Recording saved as: {new_path}")
    except Exception as e:
        print(f"[OBS] Could not rename/move file: {e}")


def listen_for_recording_stop(base_path: str):
    """
    Opens a persistent OBS event listener.
    Waits for the RecordStateChanged event and triggers on_recording_stopped.
    Runs in a background thread.
    """
    try:
        client = obs.EventClient(host=_HOST, port=_PORT, password=_PASSWORD)

        def handle_event(event):
            # RecordStateChanged fires with output_state = 'OBS_WEBSOCKET_OUTPUT_STOPPED'
            if hasattr(event, 'output_state'):
                if event.output_state == "OBS_WEBSOCKET_OUTPUT_STOPPED":
                    on_recording_stopped(base_path)

        client.callback.register(handle_event)
        print("[OBS] Listening for recording stop events...")
        return client
    except Exception as e:
        print(f"[OBS] Could not start event listener: {e}")
        return None
