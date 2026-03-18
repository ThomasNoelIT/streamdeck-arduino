import serial
import pyautogui
from src.config import BAUD

def read_arduino(get_active_buttons_fn, app_ref, get_port_fn):
    try:
        port = get_port_fn()
        ser = serial.Serial(port, BAUD, timeout=1)
        app_ref.update_status("Connecté ✅")
    except Exception:
        app_ref.update_status("Arduino non trouvé ❌")
        return

    while True:
        try:
            line = ser.readline().decode("utf-8").strip()
            if line:
                buttons = get_active_buttons_fn()
                if line in buttons:
                    btn = buttons[line]
                    action = btn.get("action", "shortcut")

                    if action == "profile":
                        # Change le profil actif
                        target = btn.get("target", "default")
                        app_ref.set_profile(target)
                    else:
                        # Raccourci clavier classique
                        shortcut = btn.get("shortcut", "")
                        if shortcut:
                            pyautogui.hotkey(*shortcut.split("+"))

                    app_ref.flash_button(line)
        except Exception:
            pass