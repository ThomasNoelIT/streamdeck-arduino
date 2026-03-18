import customtkinter as ctk
from src.config import get_active_buttons, get_profile_names, save_config

class GridMixin:

    def _build_grid(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()
        self.btn_widgets = {}
        buttons = get_active_buttons(self.config, self.profile_var.get())
        for i, key in enumerate(buttons):
            row, col = divmod(i, 3)
            btn = ctk.CTkButton(
                self.grid_frame,
                width=150, height=80,
                text=self._btn_text(key, buttons),
                font=ctk.CTkFont(size=13),
                command=lambda k=key: self.open_editor(k)
            )
            btn.grid(row=row, column=col, padx=6, pady=6)
            self.btn_widgets[key] = btn

    def _refresh_grid(self):
        buttons = get_active_buttons(self.config, self.profile_var.get())
        for key, w in self.btn_widgets.items():
            w.configure(text=self._btn_text(key, buttons))

    def _btn_text(self, key, buttons=None):
        if buttons is None:
            buttons = self._get_active_buttons()
        num  = key.split(":")[1]
        btn  = buttons[key]
        lbl  = btn["label"] or "—"
        g    = " 🌐" if btn.get("global") else ""
        sc   = f"→ {btn.get('target', '?')}" if btn.get("action") == "profile" \
               else (btn.get("shortcut") or "aucun")
        return f"BTN {num}{g}\n{lbl}\n{sc}"

    def _on_profile_select(self, value):
        self.close_editor()
        self._build_grid()

    def _update_profile_menu(self):
        names = get_profile_names(self.config)
        self.profile_menu.configure(values=names)
        self.profile_target_menu.configure(values=names)

    def _new_profile_dialog(self):
        dialog = ctk.CTkInputDialog(text="Nom du nouveau profil :", title="Nouveau profil")
        name = dialog.get_input()
        if not name or name in self.config["profiles"]:
            return
        dialog_exe = ctk.CTkInputDialog(
            text="Nom de l'exe à détecter (ex: discord.exe) — laisser vide si aucun :",
            title="Détection exe"
        )
        exe = dialog_exe.get_input() or ""
        dialog_title = ctk.CTkInputDialog(
            text="Mot-clé dans le titre de fenêtre (ex: Discord) — laisser vide si aucun :",
            title="Détection titre"
        )
        title = dialog_title.get_input() or ""
        self.config["profiles"][name] = {
            "match_exe":   exe.lower(),
            "match_title": title,
        }
        save_config(self.config)
        self.watcher.update_config(self.config)
        self._update_profile_menu()
        self.profile_var.set(name)
        self._build_grid()

    def _delete_profile(self):
        name = self.profile_var.get()
        if name == "default":
            return
        del self.config["profiles"][name]
        save_config(self.config)
        self.watcher.update_config(self.config)
        self._update_profile_menu()
        self.profile_var.set("default")
        self._build_grid()