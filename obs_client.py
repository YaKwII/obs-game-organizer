# OBS WebSocket client
# Requires OBS 28+ with WebSocket server enabled
# Tools > WebSocket Server Settings > Enable WebSocket Server

import obsws_python as obs

# These are set at runtime via configure()
_HOST = "localhost"
_PORT = 4455
_PASSWORD = ""


def configure(host: str, port: int, password: str):
    """Set OBS connection details from config."""
    global _HOST, _PORT, _PASSWORD
    _HOST = host
    _PORT = port
    _PASSWORD = password


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
