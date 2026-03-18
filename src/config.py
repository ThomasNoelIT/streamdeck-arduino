import os
import sys
import json

BASE_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "StreamDeck")
os.makedirs(BASE_DIR, exist_ok=True)  # crée le dossier s'il n'existe pas

CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

BAUD = 9600

def get_port(cfg):
    return cfg.get("port", "COM3")

def set_port(cfg, port):
    cfg["port"] = port
    save_config(cfg)

DEFAULT_BTN = {
    "BTN:1": {"label": "Mute Micro",       "shortcut": "ctrl+shift+m",  "global": False},
    "BTN:2": {"label": "Caméra",           "shortcut": "ctrl+shift+o",  "global": False},
    "BTN:3": {"label": "Bureau",           "shortcut": "win+d",         "global": False},
    "BTN:4": {"label": "Terminal",         "shortcut": "ctrl+alt+t",    "global": False},
    "BTN:5": {"label": "Capture écran",    "shortcut": "win+shift+s",   "global": True},
    "BTN:6": {"label": "Gestion. tâches",  "shortcut": "ctrl+shift+esc","global": False},
}

DEFAULT_CONFIG = {
    "port": "COM3",
    "profiles": {"default": DEFAULT_BTN}
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return json.loads(json.dumps(DEFAULT_CONFIG))  # deep copy

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

def get_active_buttons(cfg, profile_name):
    """
    Retourne les 6 boutons effectifs pour le profil donné.
    Priorité : global du default > profil actif > default.
    """
    default  = cfg["profiles"].get("default", {})
    profil   = cfg["profiles"].get(profile_name, {}) if profile_name != "default" else {}
    result   = {}

    for key in DEFAULT_BTN:
        default_btn = default.get(key, DEFAULT_BTN[key])
        # Bouton global → toujours celui du default
        if default_btn.get("global", False):
            result[key] = default_btn
        # Sinon → profil actif s'il existe, sinon default
        elif key in profil:
            result[key] = profil[key]
        else:
            result[key] = default_btn

    return result

def get_profile_names(cfg):
    return list(cfg["profiles"].keys())