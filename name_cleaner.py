import re


def clean_name(raw_name: str) -> str:
    """
    Turns a raw window title into a safe folder/file name.
    Example: 'ELDEN RING\u2122' -> 'ELDEN-RING'
    """
    # Remove trademark, copyright, and registered symbols
    cleaned = re.sub(r'[\u00ae\u00a9\u2122]', '', raw_name)
    # Replace spaces and unsafe characters with a dash
    cleaned = re.sub(r'[\s/\\:*?"<>|]+', '-', cleaned)
    # Remove leading/trailing dashes
    cleaned = cleaned.strip('-')
    # Collapse multiple dashes
    cleaned = re.sub(r'-+', '-', cleaned)
    return cleaned
