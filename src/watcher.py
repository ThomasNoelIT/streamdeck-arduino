import threading
import time

try:
    import win32gui
    import win32process
    import psutil
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

def get_active_window():
    """Retourne (exe_name, window_title) de la fenêtre active."""
    if not HAS_WIN32:
        return None, None
    try:
        hwnd  = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        exe   = psutil.Process(pid).name().lower()
        return exe, title
    except Exception:
        return None, None

def find_matching_profile(cfg, exe, title):
    """
    Cherche le profil qui correspond à la fenêtre active.
    Chaque profil (hors default) peut avoir :
      "match_exe":   "discord.exe"
      "match_title": "Discord"
    Les deux doivent matcher si les deux sont définis.
    """
    for name, profile in cfg["profiles"].items():
        if name == "default":
            continue
        match_exe   = profile.get("match_exe",   "").lower()
        match_title = profile.get("match_title", "").lower()

        exe_ok   = (not match_exe)   or (exe   and match_exe   in exe)
        title_ok = (not match_title) or (title and match_title in title.lower())

        if exe_ok and title_ok:
            return name

    return "default"

class WindowWatcher:
    """Surveille la fenêtre active et appelle on_change(profile_name) si ça change."""
    def __init__(self, cfg, on_change):
        self.cfg        = cfg
        self.on_change  = on_change
        self._current   = None
        self._running   = True
        self._thread    = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def update_config(self, cfg):
        self.cfg = cfg

    def _loop(self):
        while self._running:
            exe, title = get_active_window()
            profile    = find_matching_profile(self.cfg, exe, title)
            if profile != self._current:
                self._current = profile
                self.on_change(profile)
            time.sleep(0.5)

    def stop(self):
        self._running = False