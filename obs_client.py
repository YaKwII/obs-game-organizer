# OBS WebSocket client
# Requires OBS 28+ with WebSocket server enabled
# Tools > WebSocket Server Settings > Enable WebSocket Server

import obsws_python as obs

OBS_HOST = "localhost"
OBS_PORT = 4455
OBS_PASSWORD = ""  # Set your OBS WebSocket password here


def set_recording_directory(path: str):
    """
    Tells OBS to save recordings to the given directory path.
    """
    try:
        with obs.ReqClient(host=OBS_HOST, port=OBS_PORT, password=OBS_PASSWORD) as client:
            client.set_profile_parameter(
                "SimpleOutput", "FilePath", path
            )
            print(f"[OBS] Recording directory set to: {path}")
    except Exception as e:
        print(f"[OBS] Connection error: {e}")
        print("Make sure OBS is open and WebSocket is enabled.")
