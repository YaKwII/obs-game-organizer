import win32gui
import win32process
import psutil


def get_active_window():
    """
    Returns a dict with:
      - title: the foreground window title
      - exe: the executable name (e.g., 'cs2.exe')
    """
    try:
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        proc = psutil.Process(pid)
        exe = proc.name()  # e.g. 'cs2.exe'
        return {"title": title, "exe": exe}
    except Exception as e:
        return {"title": "", "exe": "", "error": str(e)}
