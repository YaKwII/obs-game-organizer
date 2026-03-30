# OBS Game Organizer

A Python app that detects the active game window on Windows and automatically organizes your OBS recordings into folders named after the game you are playing.

## Features
- Detects the active foreground window title and executable
- Cleans window titles into safe folder/file names
- Auto-creates game folders if they do not exist
- Custom game name mapping via `game_map.json`
- Connects to OBS via WebSocket to set the recording directory

## Project Structure
```
obs-game-organizer/
├── main.py             # App entry point and main loop
├── window_reader.py    # Reads active window title and exe path
├── name_cleaner.py     # Cleans titles into safe file/folder names
├── game_map.json       # Custom game name mappings
├── obs_client.py       # OBS WebSocket connection and commands
├── requirements.txt    # Python dependencies
└── README.md
```

## Requirements
- Windows 10/11
- Python 3.10+
- OBS Studio with WebSocket enabled (built-in since OBS 28)

## Setup
1. Clone this repo
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Enable OBS WebSocket: `Tools > WebSocket Server Settings > Enable`
4. Edit `game_map.json` to add your custom game mappings
5. Run:
   ```
   python main.py
   ```

## How It Works
1. The app reads the active foreground window every second
2. It matches the title or executable to a known game
3. It cleans the name into a safe folder name
4. It creates the folder under your chosen base recording path
5. It tells OBS (via WebSocket) to use that folder for recordings
