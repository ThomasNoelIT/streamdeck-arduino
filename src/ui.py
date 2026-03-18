import threading
import time
import customtkinter as ctk
import pyautogui
pyautogui.FAILSAFE = False
from src.config import load_config, save_config, get_active_buttons, get_profile_names
from src.arduino import read_arduino
from src.watcher import WindowWatcher
from src.ui_grid import GridMixin
from src.ui_editor import EditorMixin
from src.ui_capture import ShortcutCaptureMixin

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class StreamDeckApp(ctk.CTk, GridMixin, EditorMixin, ShortcutCaptureMixin):
    def __init__(self):
        super().__init__()
        self.title("Stream Deck")
        self.geometry("540x720")
        self.minsize(540, 620)
        self.resizable(True, True)

        self.config         = load_config()
        self.active_profile = "default"
        self.btn_widgets    = {}
        self.selected       = None
        self.action_var     = ctk.StringVar(value="shortcut")

        self._build_ui()

        self.watcher = WindowWatcher(self.config, self._on_profile_change)

        t = threading.Thread(
            target=read_arduino,
            args=(self._get_active_buttons, self, self._get_port),
            daemon=True
        )
        t.start()

    def _get_port(self):
        from src.config import get_port
        return get_port(self.config)
    
    def _get_active_buttons(self):
        return get_active_buttons(self.config, self.active_profile)

    def _on_profile_change(self, profile_name):
        self.active_profile = profile_name
        self.after(0, self._refresh_grid)
        self.after(0, lambda: self.profile_label.configure(
            text=f"Profil actif : {profile_name}"
        ))

    def set_profile(self, profile_name):
        if profile_name in self.config["profiles"]:
            self.active_profile = profile_name
            self.after(0, self._refresh_grid)
            self.after(0, lambda: self.profile_label.configure(
                text=f"Profil actif : {profile_name}"
            ))

    def flash_button(self, key):
        def _flash():
            w = self.btn_widgets.get(key)
            if w:
                w.configure(fg_color="green")
                time.sleep(0.3)
                w.configure(fg_color="#1f538d")
        threading.Thread(target=_flash, daemon=True).start()

    def update_status(self, msg):
        color = "green" if "✅" in msg else "red"
        self.status_label.configure(text=msg, text_color=color)

    def _build_ui(self):
        # Status + profil actif
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(pady=(12, 0), fill="x", padx=20)
        self.status_label = ctk.CTkLabel(top, text="Connexion...", text_color="gray")
        self.status_label.pack(side="left")
        self.profile_label = ctk.CTkLabel(
            top, text="Profil actif : default", text_color="#7c6fff"
        )
        self.profile_label.pack(side="right")

        # Sélecteur de profil
        sel_frame = ctk.CTkFrame(self, fg_color="transparent")
        sel_frame.pack(padx=20, pady=(6, 0), fill="x")
        ctk.CTkLabel(sel_frame, text="Configurer le profil :").pack(side="left", padx=(0, 8))
        self.profile_var = ctk.StringVar(value="default")
        self.profile_menu = ctk.CTkOptionMenu(
            sel_frame, variable=self.profile_var,
            values=get_profile_names(self.config),
            command=self._on_profile_select
        )
        self.profile_menu.pack(side="left")
        ctk.CTkButton(
            sel_frame, text="+ Nouveau profil", width=130,
            fg_color="transparent", border_width=1,
            command=self._new_profile_dialog
        ).pack(side="left", padx=(8, 0))
        ctk.CTkButton(
            sel_frame, text="🗑", width=36,
            fg_color="transparent", border_width=1, text_color="#ff6b6b",
            command=self._delete_profile
        ).pack(side="left", padx=(4, 0))

        self.settings_btn = ctk.CTkButton(
            top, text="⚙️", width=36,
            fg_color="transparent", border_width=1,
            command=self._open_settings
        )
        self.settings_btn.pack(side="right", padx=(0, 8))

        # Grille
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(padx=20, pady=12)
        self._build_grid()

        ctk.CTkLabel(self, text="─" * 55, text_color="gray").pack()

        # Éditeur
        self.editor_frame = ctk.CTkFrame(self)
        self.editor_frame.pack(padx=20, pady=10, fill="both", expand=True)

        self.editor_title = ctk.CTkLabel(
            self.editor_frame,
            text="Clique sur un bouton pour le configurer",
            font=ctk.CTkFont(size=13), text_color="gray"
        )
        self.editor_title.pack(pady=(10, 6))

        # Nom affiché
        ctk.CTkLabel(self.editor_frame, text="Nom affiché").pack(anchor="w", padx=16)
        self.inp_label = ctk.CTkEntry(self.editor_frame, placeholder_text="ex: Mute Micro")
        self.inp_label.pack(padx=16, pady=(2, 8), fill="x", expand=True)

        # Type d'action
        ctk.CTkLabel(self.editor_frame, text="Action").pack(anchor="w", padx=16)
        action_row = ctk.CTkFrame(self.editor_frame, fg_color="transparent")
        action_row.pack(padx=16, pady=(2, 8), fill="x")
        self.rb_shortcut = ctk.CTkRadioButton(
            action_row, text="Raccourci clavier",
            variable=self.action_var, value="shortcut",
            command=self._on_action_type_change
        )
        self.rb_shortcut.pack(side="left", padx=(0, 16))
        self.rb_profile = ctk.CTkRadioButton(
            action_row, text="Changer de profil",
            variable=self.action_var, value="profile",
            command=self._on_action_type_change
        )
        self.rb_profile.pack(side="left")

        # Champ raccourci
        self.shortcut_frame = ctk.CTkFrame(self.editor_frame, fg_color="transparent")
        self.shortcut_frame.pack(padx=16, pady=(2, 4), fill="x", expand=True)
        ctk.CTkLabel(self.shortcut_frame, text="Raccourci").pack(anchor="w")
        sc_row = ctk.CTkFrame(self.shortcut_frame, fg_color="transparent")
        sc_row.pack(pady=(2, 4), fill="x", expand=True)
        self.inp_shortcut = ctk.CTkEntry(sc_row, placeholder_text="Clique sur Capturer...")
        self.inp_shortcut.configure(state="readonly")
        self.inp_shortcut.pack(side="left", padx=(0, 8), fill="x", expand=True)
        self.capture_btn = ctk.CTkButton(
            sc_row, text="🎹 Capturer", width=130,
            fg_color="#2d6a2d", hover_color="#3a8a3a",
            command=self.start_capture
        )
        self.capture_btn.pack(side="left")

        # Champ profil cible
        self.profile_target_frame = ctk.CTkFrame(self.editor_frame, fg_color="transparent")
        ctk.CTkLabel(self.profile_target_frame, text="Profil cible").pack(anchor="w")
        self.profile_target_var = ctk.StringVar(value="default")
        self.profile_target_menu = ctk.CTkOptionMenu(
            self.profile_target_frame,
            variable=self.profile_target_var,
            values=get_profile_names(self.config)
        )
        self.profile_target_menu.pack(fill="x", pady=(2, 0))

        # Hint + global + boutons
        self.capture_hint = ctk.CTkLabel(
            self.editor_frame, text="",
            font=ctk.CTkFont(size=11), text_color="gray"
        )
        self.capture_hint.pack(padx=16)

        self.global_var = ctk.BooleanVar(value=False)
        self.global_chk = ctk.CTkCheckBox(
            self.editor_frame, text="Toujours actif (global)",
            variable=self.global_var
        )
        self.global_chk.pack(anchor="w", padx=16, pady=(4, 0))

        btn_row = ctk.CTkFrame(self.editor_frame, fg_color="transparent")
        btn_row.pack(padx=16, pady=(8, 12))
        self.save_btn = ctk.CTkButton(btn_row, text="Enregistrer", width=140, command=self.save)
        self.save_btn.grid(row=0, column=0, padx=6)
        self.test_btn = ctk.CTkButton(
            btn_row, text="Tester ▶", width=120,
            fg_color="transparent", border_width=1, command=self.test
        )
        self.test_btn.grid(row=0, column=1, padx=6)
        self.cancel_btn = ctk.CTkButton(
            btn_row, text="Annuler", width=100,
            fg_color="transparent", text_color="gray", command=self.close_editor
        )
        self.cancel_btn.grid(row=0, column=2, padx=6)

        self._set_editor_active(False)

    def _open_settings(self):
        from src.config import get_port, set_port
        import serial.tools.list_ports

        win = ctk.CTkToplevel(self)
        win.title("Paramètres")
        win.geometry("380x220")
        win.resizable(False, False)
        win.grab_set()

        ctk.CTkLabel(win, text="Port série Arduino",
                    font=ctk.CTkFont(size=14)).pack(pady=(20, 4))

        ports_dispo = [p.device for p in serial.tools.list_ports.comports()]
        if not ports_dispo:
            ports_dispo = ["COM1", "COM2", "COM3", "COM4", "COM5"]

        port_var = ctk.StringVar(value=get_port(self.config))
        port_menu = ctk.CTkOptionMenu(win, variable=port_var, values=ports_dispo)
        port_menu.pack(pady=4, padx=40, fill="x")

        def refresh_ports():
            new_ports = [p.device for p in serial.tools.list_ports.comports()]
            if new_ports:
                port_menu.configure(values=new_ports)
                port_var.set(new_ports[0])

        ctk.CTkButton(
            win, text="🔄 Rafraîchir les ports", width=180,
            fg_color="transparent", border_width=1,
            command=refresh_ports
        ).pack(pady=(4, 12))

        def save_and_close():
            set_port(self.config, port_var.get())
            self.update_status(f"Port changé → {port_var.get()} (redémarre l'app)")
            win.destroy()

        ctk.CTkButton(win, text="Enregistrer", command=save_and_close).pack(pady=(0, 8))

        ctk.CTkLabel(
            win,
            text="⚠️ Redémarre l'application pour appliquer le changement",
            font=ctk.CTkFont(size=11), text_color="gray"
        ).pack()