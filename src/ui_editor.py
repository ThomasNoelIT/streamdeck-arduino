import customtkinter as ctk
import pyautogui
from src.config import save_config, get_active_buttons, get_profile_names

class EditorMixin:
    """Mixin gérant le panneau d'édition d'un bouton."""

    def _on_action_type_change(self):
        if self.action_var.get() == "shortcut":
            self.profile_target_frame.pack_forget()
            self.shortcut_frame.pack(padx=16, pady=(2, 4), fill="x", expand=True)
        else:
            self.shortcut_frame.pack_forget()
            self.profile_target_frame.pack(padx=16, pady=(2, 4), fill="x")

    def _set_editor_active(self, active):
        state = "normal" if active else "disabled"
        self.inp_label.configure(state=state)
        self.save_btn.configure(state=state)
        self.test_btn.configure(state=state)
        self.cancel_btn.configure(state=state)
        self.capture_btn.configure(state=state)
        self.global_chk.configure(state=state)
        self.rb_shortcut.configure(state=state)
        self.rb_profile.configure(state=state)
        self.profile_target_menu.configure(state=state)

    def open_editor(self, key):
        self.selected = key
        editing_profile = self.profile_var.get()
        buttons = get_active_buttons(self.config, editing_profile)
        num = key.split(":")[1]
        self.editor_title.configure(
            text=f"Configurer BTN {num} — profil « {editing_profile} »",
            text_color="white"
        )
        btn = buttons[key]
        self.action_var.set(btn.get("action", "shortcut"))

        self.inp_label.configure(state="normal")
        self.inp_shortcut.configure(state="normal")
        self.inp_label.delete(0, "end")
        self.inp_shortcut.delete(0, "end")
        self.inp_label.insert(0, btn["label"])
        self.inp_shortcut.insert(0, btn.get("shortcut", ""))
        self.inp_shortcut.configure(state="readonly")

        self.profile_target_var.set(btn.get("target", "default"))
        self.profile_target_menu.configure(values=get_profile_names(self.config))

        self._on_action_type_change()
        self.global_var.set(btn.get("global", False))
        self._set_editor_active(True)

        for k, w in self.btn_widgets.items():
            w.configure(fg_color=("#3a7ebf" if k == key else "#1f538d"))

    def close_editor(self):
        self.selected = None
        self.editor_title.configure(
            text="Clique sur un bouton pour le configurer", text_color="gray"
        )
        self._set_editor_active(False)
        for w in self.btn_widgets.values():
            w.configure(fg_color="#1f538d")

    def save(self):
        if not self.selected:
            return
        label = self.inp_label.get().strip()[:50]
        if "\n" in label:
            return

        action          = self.action_var.get()
        editing_profile = self.profile_var.get()
        profile         = self.config["profiles"].setdefault(editing_profile, {})

        if action == "profile":
            profile[self.selected] = {
                "label":    label,
                "action":   "profile",
                "target":   self.profile_target_var.get(),
                "shortcut": "",
                "global":   self.global_var.get(),
            }
        else:
            self.inp_shortcut.configure(state="normal")
            shortcut = self.inp_shortcut.get().strip()[:50]
            self.inp_shortcut.configure(state="readonly")
            if "\n" in shortcut:
                return
            profile[self.selected] = {
                "label":    label,
                "action":   "shortcut",
                "shortcut": shortcut,
                "global":   self.global_var.get(),
            }

        save_config(self.config)
        self.watcher.update_config(self.config)
        self._refresh_grid()
        self.close_editor()

    def test(self):
        if self.action_var.get() == "profile":
            self.set_profile(self.profile_target_var.get())
            return
        self.inp_shortcut.configure(state="normal")
        sc = self.inp_shortcut.get()
        self.inp_shortcut.configure(state="readonly")
        if sc:
            try:
                pyautogui.hotkey(*sc.split("+"))
            except Exception:
                pass