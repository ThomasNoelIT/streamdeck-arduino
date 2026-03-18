from pynput import keyboard as pynput_kb

MODS = {
    pynput_kb.Key.ctrl_l, pynput_kb.Key.ctrl_r,
    pynput_kb.Key.shift_l, pynput_kb.Key.shift_r,
    pynput_kb.Key.alt_l, pynput_kb.Key.alt_r, pynput_kb.Key.alt_gr,
    pynput_kb.Key.cmd, pynput_kb.Key.cmd_l, pynput_kb.Key.cmd_r,
}

MOD_NAMES = {
    pynput_kb.Key.ctrl_l:  "ctrl", pynput_kb.Key.ctrl_r:  "ctrl",
    pynput_kb.Key.shift_l: "shift", pynput_kb.Key.shift_r: "shift",
    pynput_kb.Key.alt_l:   "alt",  pynput_kb.Key.alt_r:   "alt",
    pynput_kb.Key.alt_gr:  "alt",
    pynput_kb.Key.cmd:     "win",  pynput_kb.Key.cmd_l:   "win",
    pynput_kb.Key.cmd_r:   "win",
}

KEY_MAP = {
    "space": "space", "enter": "enter", "return": "enter",
    "tab": "tab", "backspace": "backspace", "delete": "delete",
    "esc": "esc", "escape": "esc",
    "up": "up", "down": "down", "left": "left", "right": "right",
    "home": "home", "end": "end",
    "page_up": "pageup", "page_down": "pagedown",
    "f1": "f1", "f2": "f2", "f3": "f3", "f4": "f4",
    "f5": "f5", "f6": "f6", "f7": "f7", "f8": "f8",
    "f9": "f9", "f10": "f10", "f11": "f11", "f12": "f12",
    "media_play_pause": "playpause", "media_next": "nexttrack",
    "media_previous": "prevtrack", "media_volume_up": "volumeup",
    "media_volume_down": "volumedown", "media_volume_mute": "volumemute",
}

class ShortcutCaptureMixin:
    """Mixin à intégrer dans StreamDeckApp pour la capture de raccourcis."""

    def start_capture(self):
        self.capture_hint.configure(text="⏺ Appuie sur ton raccourci...", text_color="orange")
        self.capture_btn.configure(text="En attente...", state="disabled", fg_color="#555")
        self._pressed_keys = set()
        self._listener = pynput_kb.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self._listener.start()

    def _on_key_press(self, key):
        self._pressed_keys.add(key)

    def _on_key_release(self, key):
        if not self._pressed_keys:
            return

        parts = []
        seen_mods = []
        for mod in [pynput_kb.Key.ctrl_l, pynput_kb.Key.ctrl_r,
                    pynput_kb.Key.shift_l, pynput_kb.Key.shift_r,
                    pynput_kb.Key.alt_l,   pynput_kb.Key.alt_r,
                    pynput_kb.Key.cmd,     pynput_kb.Key.cmd_l]:
            if mod in self._pressed_keys:
                name = MOD_NAMES[mod]
                if name not in seen_mods:
                    seen_mods.append(name)
                    parts.append(name)

        main = None
        for k in self._pressed_keys:
            if k not in MODS:
                main = k
                break

        if main:
            ctrl_held = any(m in self._pressed_keys for m in [
                pynput_kb.Key.ctrl_l, pynput_kb.Key.ctrl_r
            ])
            char_ok = (
                hasattr(main, 'char') and main.char
                and main.char.isprintable() and not ctrl_held
            )
            if char_ok:
                parts.append(main.char.lower())
            elif ctrl_held and hasattr(main, 'vk') and main.vk:
                parts.append(chr(main.vk).lower())
            elif hasattr(main, 'vk') and main.vk:
                parts.append(chr(main.vk).lower())
            else:
                raw = str(main).replace("Key.", "")
                parts.append(KEY_MAP.get(raw, raw))

        shortcut = "+".join(parts)
        self._listener.stop()
        self._pressed_keys = set()
        self.after(0, lambda: self._apply_capture(shortcut))

    def _apply_capture(self, shortcut):
        self.inp_shortcut.configure(state="normal")
        self.inp_shortcut.delete(0, "end")
        self.inp_shortcut.insert(0, shortcut)
        self.inp_shortcut.configure(state="readonly")
        self.capture_btn.configure(text="🎹 Capturer", state="normal", fg_color="#2d6a2d")
        self.capture_hint.configure(text=f"✅ Capturé : {shortcut}", text_color="green")