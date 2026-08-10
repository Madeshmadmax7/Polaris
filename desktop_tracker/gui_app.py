"""
LifeOS Desktop Agent — GUI Application
Premium dark-themed desktop app matching the POLARIS web frontend.
Built with CustomTkinter.
"""

import os
import sys
import threading
import time
import tkinter as tk
import ctypes

import customtkinter as ctk
from PIL import Image, ImageDraw

from api_client import LifeOSClient
from blocker import AppBlocker
from block_overlay import set_app_root
from main import TrackingEngine
from tray import SystemTray
from command_dock import CommandDock
import keyboard

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

BG          = "#000000"
PANEL       = "#0a0a0a"
CARD        = "#111111"
CARD_BORDER = "#1a1a1a"
ACCENT      = "#ffffff"
TEXT_PRIMARY = "#ffffff"
TEXT_MUTED   = "#71717a"   # zinc-500
TEXT_DIM     = "#3f3f46"   # zinc-700
GREEN        = "#22c55e"
RED          = "#ef4444"
NEUTRAL_CLR  = "#71717a"
INPUT_BG     = "#0d0d0d"
INPUT_BORDER = "#1a1a1a"

FONT_FAMILY = "Segoe UI"  # Fallback for Outfit; looks great on Windows


def _make_round_icon(size=128):
    """Create a round LifeOS icon for the window."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, 4, size - 4, size - 4], fill=(10, 10, 26))
    draw.ellipse([16, 16, size - 16, size - 16], outline=(255, 255, 255), width=2)
    return img


# ══════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ══════════════════════════════════════════════════════════════

class LifeOSApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("POLARIS — Desktop Agent")
        self.geometry("550x850")
        self.minsize(500, 750)
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self._hide_to_tray)

        # Set icon
        icon = _make_round_icon()
        self._photo = ctk.CTkImage(light_image=icon, dark_image=icon, size=(32, 32))

        # Core services
        self.client = LifeOSClient()
        self.blocker = AppBlocker(api_client=self.client)
        self.engine = TrackingEngine(client=self.client, blocker=self.blocker)
        self.tray = SystemTray(
            on_open=self._show_window,
            on_pause=lambda: self.engine.pause(),
            on_resume=lambda: self.engine.resume(),
            on_quit=self._quit,
        )

        self._current_frame = None

        # Register root for block overlay (thread-safe)
        set_app_root(self)

        # Initialize Command Dock
        self.command_dock = CommandDock(self, self._handle_dock_command)
        
        # Register global hotkey
        try:
            keyboard.add_hotkey('alt+space', self._on_hotkey)
        except Exception as e:
            print("Warning: Failed to bind alt+space hotkey:", e)

        # Auto-login check
        if self.client.verify_session():
            self._check_admin_and_proceed()
        else:
            self._show_login()

    def _on_hotkey(self):
        # Must be called on the main thread
        self.after(0, self.command_dock.toggle)

    def _handle_dock_command(self, action: str):
        if action == "focus-25":
            self.client.start_focus_session(25)
            self.blocker.focus_mode = True
            # Update GUI switch if we are on dashboard
            if isinstance(self._current_frame, DashboardScreen):
                self._current_frame.focus_var.set("on")
        elif action == "focus-50":
            self.client.start_focus_session(50)
            self.blocker.focus_mode = True
            if isinstance(self._current_frame, DashboardScreen):
                self._current_frame.focus_var.set("on")
        elif action == "block":
            self.blocker.distraction_blocker_enabled = True
            if isinstance(self._current_frame, DashboardScreen):
                self._current_frame.dist_blocker_var.set("on")
        elif action == "unblock":
            self.blocker.distraction_blocker_enabled = False
            if isinstance(self._current_frame, DashboardScreen):
                self._current_frame.dist_blocker_var.set("off")
        elif action == "stats":
            self._show_window()

    # ── Window Management ────────────────────────────────────

    def _hide_to_tray(self):
        self.withdraw()
        if not self.tray._thread or not self.tray._thread.is_alive():
            self.tray.start()

    def _show_window(self):
        self.after(0, self.deiconify)
        self.after(0, self.lift)
        self.after(0, self.focus_force)

    def _quit(self):
        self.engine.stop()
        self.blocker.stop_sync()
        self.tray.stop()
        self.destroy()
        os._exit(0)

    # ── Screen Navigation ────────────────────────────────────

    def _switch(self, frame_cls):
        if self._current_frame:
            self._current_frame.destroy()
        self._current_frame = frame_cls(self)
        self._current_frame.pack(fill="both", expand=True)

    def _show_login(self):
        self._switch(LoginScreen)

    def _check_admin_and_proceed(self):
        """Check for administrator privileges. If not admin, trigger UAC prompt."""
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        except:
            is_admin = False

        if is_admin:
            self._show_dashboard()
        else:
            # Trigger UAC Prompt
            if getattr(sys, 'frozen', False):
                # Running as PyInstaller executable
                executable = sys.executable
                args = " ".join(sys.argv[1:])
            else:
                # Running from Python script
                executable = sys.executable
                args = f'"{os.path.abspath(sys.argv[0])}" ' + " ".join(sys.argv[1:])

            ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, args, None, 1)
            
            # If ShellExecuteW succeeds, it returns a value > 32. 
            # We then exit the current un-elevated process.
            if ret > 32:
                sys.exit(0)
            else:
                # User denied UAC or it failed. Fallback to dashboard without admin rights.
                self._show_dashboard()

    def _show_dashboard(self):
        self._switch(DashboardScreen)
        if not self.engine.is_running:
            self.engine.start()
        self.blocker.start_sync()
        self.tray.start()


# ══════════════════════════════════════════════════════════════
#  LOGIN SCREEN — Matches POLARIS LoginPage.jsx exactly
# ══════════════════════════════════════════════════════════════

class LoginScreen(ctk.CTkFrame):
    def __init__(self, master: LifeOSApp):
        super().__init__(master, fg_color=BG)
        self.app = master

        # Spacer
        ctk.CTkLabel(self, text="", height=80, fg_color=BG).pack()

        # POLARIS Logo
        ctk.CTkLabel(
            self, text="POLARIS",
            font=(FONT_FAMILY, 36, "normal"),
            text_color=TEXT_PRIMARY,
        ).pack(pady=(0, 4))

        # Subtitle: "Access Portal"
        ctk.CTkLabel(
            self, text="ACCESS PORTAL",
            font=(FONT_FAMILY, 18, "normal"),
            text_color=TEXT_PRIMARY,
        ).pack(pady=(0, 4))

        # Sub-subtitle
        ctk.CTkLabel(
            self, text="INITIALIZE AUTHENTICATED SESSION",
            font=(FONT_FAMILY, 8, "bold"),
            text_color=TEXT_DIM,
        ).pack(pady=(0, 40))

        # Error label (hidden initially)
        self.error_frame = ctk.CTkFrame(self, fg_color=BG, height=0)
        self.error_frame.pack(fill="x", padx=50)
        self.error_label = ctk.CTkLabel(
            self.error_frame, text="",
            font=(FONT_FAMILY, 9, "bold"),
            text_color=BG,
            fg_color=ACCENT,
            corner_radius=16,
            height=40,
        )

        # Email field
        ctk.CTkLabel(
            self, text="IDENTIFIER",
            font=(FONT_FAMILY, 8, "bold"),
            text_color=TEXT_DIM,
            anchor="w",
        ).pack(fill="x", padx=55, pady=(0, 4))

        self.email_entry = ctk.CTkEntry(
            self, placeholder_text="entity@neural-link.com",
            width=360, height=50,
            fg_color=INPUT_BG,
            border_color=INPUT_BORDER,
            border_width=1,
            corner_radius=20,
            font=(FONT_FAMILY, 12),
            text_color=TEXT_PRIMARY,
            placeholder_text_color=TEXT_DIM,
        )
        self.email_entry.pack(padx=50, pady=(0, 16))

        # Password field
        ctk.CTkLabel(
            self, text="SECURITY KEY",
            font=(FONT_FAMILY, 8, "bold"),
            text_color=TEXT_DIM,
            anchor="w",
        ).pack(fill="x", padx=55, pady=(0, 4))

        self.pass_entry = ctk.CTkEntry(
            self, placeholder_text="\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022",
            width=360, height=50, show="*",
            fg_color=INPUT_BG,
            border_color=INPUT_BORDER,
            border_width=1,
            corner_radius=20,
            font=(FONT_FAMILY, 12),
            text_color=TEXT_PRIMARY,
            placeholder_text_color=TEXT_DIM,
        )
        self.pass_entry.pack(padx=50, pady=(0, 30))

        # Submit Button — white pill, black text (exactly like frontend)
        self.login_btn = ctk.CTkButton(
            self, text="AUTHORIZE SESSION    \u2192",
            width=360, height=55,
            fg_color=ACCENT,
            text_color=BG,
            hover_color="#e4e4e7",
            corner_radius=28,
            font=(FONT_FAMILY, 11, "bold"),
            command=self._do_login,
        )
        self.login_btn.pack(padx=50)

        # Divider + Version
        ctk.CTkFrame(self, fg_color=INPUT_BORDER, height=1).pack(fill="x", padx=50, pady=(50, 0))
        ctk.CTkLabel(
            self, text="POLARIS DESKTOP AGENT v1.0.0",
            font=(FONT_FAMILY, 8, "bold"),
            text_color=TEXT_DIM,
        ).pack(pady=(12, 0))

    def _do_login(self):
        email = self.email_entry.get().strip()
        pwd = self.pass_entry.get().strip()
        if not email or not pwd:
            self._show_error("IDENTIFIER AND SECURITY KEY REQUIRED")
            return

        self.login_btn.configure(state="disabled", text="DECRYPTING...")
        self.update()

        def _task():
            ok, msg = self.app.client.login_with_credentials(email, pwd)
            self.app.after(0, self._on_result, ok, msg)

        threading.Thread(target=_task, daemon=True).start()

    def _on_result(self, ok, msg):
        self.login_btn.configure(state="normal", text="AUTHORIZE SESSION    \u2192")
        if ok:
            self.app._check_admin_and_proceed()
        else:
            self._show_error(f"CORE FAULT: {msg.upper()}")

    def _show_error(self, text):
        self.error_label.configure(text=f"  {text}  ")
        self.error_label.pack(fill="x", padx=0, pady=(0, 16))

# ══════════════════════════════════════════════════════════════
#  DASHBOARD SCREEN — Live tracking status
# ══════════════════════════════════════════════════════════════

class DashboardScreen(ctk.CTkFrame):
    def __init__(self, master: LifeOSApp):
        super().__init__(master, fg_color=BG)
        self.app = master

        # ── Header bar ───
        header = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=0, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        username = self.app.client.user_info.get("username", "Entity")
        ctk.CTkLabel(
            header, text=f"POLA",
            font=(FONT_FAMILY, 18, "normal"),
            text_color=TEXT_PRIMARY,
        ).pack(side="left", padx=(20, 0), pady=20)
        ctk.CTkLabel(
            header, text=f"RIS",
            font=(FONT_FAMILY, 18, "bold"),
            text_color=TEXT_PRIMARY,
        ).pack(side="left", pady=20)

        # Tracking toggle
        self.track_var = ctk.StringVar(value="on")
        self.toggle = ctk.CTkSwitch(
            header, text="", variable=self.track_var,
            onvalue="on", offvalue="off",
            command=self._toggle_tracking,
            progress_color=GREEN,
            width=48,
        )
        self.toggle.pack(side="right", padx=20, pady=20)

        self.status_pill = ctk.CTkLabel(
            header, text="ACTIVE",
            font=(FONT_FAMILY, 8, "bold"),
            text_color=GREEN,
        )
        self.status_pill.pack(side="right", pady=20)

        # ── Scrollable content ───
        content = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0)
        content.pack(fill="both", expand=True, padx=0, pady=0)

        # Breadcrumb
        ctk.CTkLabel(
            content, text="NEURAL / DESKTOP / LIVE",
            font=(FONT_FAMILY, 8, "bold"),
            text_color=TEXT_DIM, anchor="w",
        ).pack(fill="x", padx=24, pady=(20, 4))

        ctk.CTkLabel(
            content, text=f"Welcome back, {username}",
            font=(FONT_FAMILY, 22, "normal"),
            text_color=TEXT_PRIMARY, anchor="w",
        ).pack(fill="x", padx=24, pady=(0, 20))

        # ── Current Activity Card ───
        activity_card = ctk.CTkFrame(content, fg_color=CARD, corner_radius=24, border_width=1, border_color=CARD_BORDER)
        activity_card.pack(fill="x", padx=20, pady=(0, 12))

        ctk.CTkLabel(
            activity_card, text="CURRENTLY TRACKING",
            font=(FONT_FAMILY, 8, "bold"),
            text_color=TEXT_DIM, anchor="w",
        ).pack(fill="x", padx=24, pady=(20, 0))

        self.lbl_app = ctk.CTkLabel(
            activity_card, text="Initializing...",
            font=(FONT_FAMILY, 28, "normal"),
            text_color=TEXT_PRIMARY, anchor="w",
        )
        self.lbl_app.pack(fill="x", padx=24, pady=(4, 0))

        self.lbl_title = ctk.CTkLabel(
            activity_card, text="Waiting for window detection...",
            font=(FONT_FAMILY, 11),
            text_color=TEXT_MUTED, anchor="w",
            wraplength=380,
        )
        self.lbl_title.pack(fill="x", padx=24, pady=(2, 0))

        # Session timer — large
        self.lbl_timer = ctk.CTkLabel(
            activity_card, text="00:00",
            font=(FONT_FAMILY, 48, "normal"),
            text_color=TEXT_PRIMARY, anchor="w",
        )
        self.lbl_timer.pack(fill="x", padx=24, pady=(8, 4))

        # Category badge
        self.lbl_cat = ctk.CTkLabel(
            activity_card, text="  NEUTRAL  ",
            font=(FONT_FAMILY, 8, "bold"),
            text_color=BG,
            fg_color=NEUTRAL_CLR,
            corner_radius=12,
            height=24,
            anchor="w",
        )
        self.lbl_cat.pack(anchor="w", padx=24, pady=(0, 20))

        # ── Focus Mode & Distraction Blocker Card ───
        focus_card = ctk.CTkFrame(content, fg_color=CARD, corner_radius=24, border_width=1, border_color=CARD_BORDER)
        focus_card.pack(fill="x", padx=20, pady=(0, 12))

        # Focus Mode Switch
        focus_inner = ctk.CTkFrame(focus_card, fg_color="transparent")
        focus_inner.pack(fill="x", padx=24, pady=(16, 8))

        ctk.CTkLabel(
            focus_inner, text="FOCUS MODE",
            font=(FONT_FAMILY, 9, "bold"),
            text_color=TEXT_PRIMARY, anchor="w",
        ).pack(side="left")

        self.focus_var = ctk.StringVar(value="off")
        ctk.CTkSwitch(
            focus_inner, text="", variable=self.focus_var,
            onvalue="on", offvalue="off",
            command=self._toggle_focus,
            progress_color=GREEN, width=48,
        ).pack(side="right")

        # Distraction Blocker Switch
        dist_inner = ctk.CTkFrame(focus_card, fg_color="transparent")
        dist_inner.pack(fill="x", padx=24, pady=(4, 12))

        ctk.CTkLabel(
            dist_inner, text="DISTRACTION BLOCKER",
            font=(FONT_FAMILY, 9, "bold"),
            text_color=TEXT_PRIMARY, anchor="w",
        ).pack(side="left")

        self.dist_blocker_var = ctk.StringVar(value="on")
        ctk.CTkSwitch(
            dist_inner, text="", variable=self.dist_blocker_var,
            onvalue="on", offvalue="off",
            command=self._toggle_distraction_blocker,
            progress_color=GREEN, width=48,
        ).pack(side="right")

        ctk.CTkLabel(
            focus_card, text="Terminates all games, social media, and distracting apps automatically.",
            font=(FONT_FAMILY, 10),
            text_color=TEXT_MUTED, anchor="w",
            wraplength=380,
        ).pack(fill="x", padx=24, pady=(0, 8))

        # Block app manual entry
        add_frame = ctk.CTkFrame(focus_card, fg_color="transparent")
        add_frame.pack(fill="x", padx=24, pady=(0, 12))

        self.add_app_entry = ctk.CTkEntry(
            add_frame, placeholder_text="e.g. steam.exe or discord.exe",
            height=36, fg_color=INPUT_BG, border_color=INPUT_BORDER,
            border_width=1, corner_radius=12, font=(FONT_FAMILY, 10),
            text_color=TEXT_PRIMARY, placeholder_text_color=TEXT_DIM,
        )
        self.add_app_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            add_frame, text="BLOCK APP", height=36, width=90,
            fg_color=ACCENT, text_color=BG, hover_color="#e4e4e7",
            corner_radius=12, font=(FONT_FAMILY, 9, "bold"),
            command=self._add_custom_block,
        ).pack(side="right")

        self.lbl_blocked = ctk.CTkLabel(
            focus_card, text="APPS BLOCKED: 0",
            font=(FONT_FAMILY, 8, "bold"),
            text_color=RED, anchor="w",
        )
        self.lbl_blocked.pack(fill="x", padx=24, pady=(0, 16))

        # ── Stats Grid ───
        ctk.CTkLabel(
            content, text="SESSION METRICS",
            font=(FONT_FAMILY, 8, "bold"),
            text_color=TEXT_DIM, anchor="w",
        ).pack(fill="x", padx=24, pady=(12, 8))

        stats_grid = ctk.CTkFrame(content, fg_color="transparent")
        stats_grid.pack(fill="x", padx=20)
        stats_grid.columnconfigure(0, weight=1)
        stats_grid.columnconfigure(1, weight=1)
        stats_grid.columnconfigure(2, weight=1)

        self.stat_prod = self._make_stat_card(stats_grid, "PRODUCTIVE", "0m", GREEN, 0)
        self.stat_dist = self._make_stat_card(stats_grid, "DISTRACTING", "0m", RED, 1)
        self.stat_neut = self._make_stat_card(stats_grid, "NEUTRAL", "0m", NEUTRAL_CLR, 2)

        # ── Version footer ───
        ctk.CTkLabel(
            content, text="POLARIS DESKTOP AGENT v1.0.0",
            font=(FONT_FAMILY, 7, "bold"),
            text_color=TEXT_DIM,
        ).pack(pady=(20, 10))

        # Start live update
        self._tick()

    def _make_stat_card(self, parent, title, value, color, col):
        card = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=20, border_width=1, border_color=CARD_BORDER)
        card.grid(row=0, column=col, padx=4, pady=4, sticky="nsew")

        ctk.CTkLabel(
            card, text=title,
            font=(FONT_FAMILY, 7, "bold"),
            text_color=TEXT_DIM,
        ).pack(pady=(14, 2))

        lbl = ctk.CTkLabel(
            card, text=value,
            font=(FONT_FAMILY, 20, "normal"),
            text_color=color,
        )
        lbl.pack(pady=(0, 14))
        return lbl

    def _toggle_tracking(self):
        if self.track_var.get() == "on":
            self.app.engine.resume()
            self.status_pill.configure(text="ACTIVE", text_color=GREEN)
            self.app.tray.update_status("active")
        else:
            self.app.engine.pause()
            self.status_pill.configure(text="PAUSED", text_color="#facc15")
            self.app.tray.update_status("paused")

    def _toggle_focus(self):
        self.app.blocker.focus_mode = (self.focus_var.get() == "on")

    def _toggle_distraction_blocker(self):
        self.app.blocker.distraction_blocker_enabled = (self.dist_blocker_var.get() == "on")

    def _add_custom_block(self):
        app_exe = self.add_app_entry.get().strip()
        if app_exe:
            self.app.blocker.add_blocked_app(app_exe)
            self.add_app_entry.delete(0, 'end')

    def _tick(self):
        """Update dashboard every second with live data."""
        s = self.app.engine.get_status()

        app_name = s["app"] or "Desktop"
        cat = s["category"] or "neutral"
        title = s["title"] or "No active window"

        # Category color
        cat_colors = {"productive": GREEN, "distracting": RED, "neutral": NEUTRAL_CLR}
        cat_color = cat_colors.get(cat, NEUTRAL_CLR)

        if s["is_paused"]:
            self.lbl_app.configure(text="TRACKING PAUSED", text_color=TEXT_MUTED)
            self.lbl_title.configure(text="Resume tracking to continue monitoring.")
        else:
            self.lbl_app.configure(text=app_name, text_color=TEXT_PRIMARY)
            self.lbl_title.configure(text=title[:80])

        # Timer
        m, sec = divmod(s["session_seconds"], 60)
        h, m = divmod(m, 60)
        if h > 0:
            self.lbl_timer.configure(text=f"{h:02d}:{m:02d}:{sec:02d}")
        else:
            self.lbl_timer.configure(text=f"{m:02d}:{sec:02d}")

        # Category badge
        self.lbl_cat.configure(
            text=f"  {cat.upper()}  ",
            fg_color=cat_color,
            text_color=BG if cat != "neutral" else TEXT_PRIMARY,
        )

        # Stats
        self.stat_prod.configure(text=f"{s['total_productive'] // 60}m")
        self.stat_dist.configure(text=f"{s['total_distracting'] // 60}m")
        self.stat_neut.configure(text=f"{s['total_neutral'] // 60}m")

        # Blocked count
        self.lbl_blocked.configure(text=f"APPS BLOCKED: {s['apps_blocked']}")

        self.after(1000, self._tick)


# ══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = LifeOSApp()
    app.mainloop()
