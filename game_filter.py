# List of known game executable names to watch for.
# Add more exe names here as you play new games.
# These are matched against the active window's exe name (case-insensitive).

KNOWN_GAME_EXES = [
    "cs2",
    "csgo",
    "valorant",
    "fortnite",
    "minecraft",
    "eldenring",
    "RocketLeague",
    "EscapeFromTarkov",
    "RainbowSix",
    "overwatch",
    "gta5",
    "Cyberpunk2077",
    "destiny2",
    "apexlegends",
    "tf2",
    "dota2",
    "leagueoflegends",
    "r5apex",
    "javaw",       # Minecraft Java
    "bedrocklauncher",
    "steam",
]


def is_game_window(window_info: dict) -> bool:
    """
    Returns True only if the active window looks like a game.
    Checks the exe name against the known games list.
    """
    exe = window_info.get("exe", "").lower().replace(".exe", "")
    title = window_info.get("title", "").lower()

    if not exe and not title:
        return False

    for known in KNOWN_GAME_EXES:
        if known.lower() in exe:
            return True

    return False
