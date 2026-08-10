"""
LifeOS Desktop Tracker — Command Dock
A floating, Spotlight-style command palette triggered by Alt+Space.
"""

import tkinter as tk
import customtkinter as ctk

BG          = "#0a0a0a"
INPUT_BG    = "transparent"
TEXT_PRIMARY= "#ffffff"
TEXT_MUTED  = "#a1a1aa"
TEXT_DIM    = "#3f3f46"
HOVER_BG    = "#1a1a1a"
FONT_FAMILY = "Segoe UI"

COMMANDS = [
    {"id": "focus25", "label": "Start 25 Min Focus Sprint", "category": "Focus", "action": "focus-25"},
    {"id": "focus50", "label": "Start 50 Min Deep Work", "category": "Focus", "action": "focus-50"},
    {"id": "block", "label": "Block Distracting Sites", "category": "Blocking", "action": "block"},
    {"id": "unblock", "label": "Unblock All Sites", "category": "Blocking", "action": "unblock"},
    {"id": "stats", "label": "Show Today's Stats", "category": "Stats", "action": "stats"},
]

class CommandDock(ctk.CTkToplevel):
    def __init__(self, master, on_command_callback):
        super().__init__(master)
        
        self.on_command_callback = on_command_callback
        
        # Setup window as frameless, floating, always-on-top
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.geometry("440x300")
        
        # Center on screen
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width / 2) - (440 / 2))
        y = int(screen_height * 0.2) # 20% down from top
        self.geometry(f"+{x}+{y}")
        
        # Main container with dark styling
        self.container = ctk.CTkFrame(
            self, 
            fg_color=BG,
            corner_radius=20,
            border_width=1,
            border_color="rgba(255,255,255,0.1)"
        )
        self.container.pack(fill="both", expand=True)
        
        # Search area
        self.search_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.search_frame.pack(fill="x", padx=18, pady=(14, 14))
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_change)
        
        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            textvariable=self.search_var,
            placeholder_text="Type a command...",
            fg_color=INPUT_BG,
            border_width=0,
            font=(FONT_FAMILY, 16),
            text_color=TEXT_PRIMARY,
            placeholder_text_color=TEXT_DIM,
            height=30
        )
        self.search_entry.pack(side="left", fill="x", expand=True)
        
        # ESC hint
        esc_hint = ctk.CTkLabel(
            self.search_frame, 
            text="ESC", 
            font=(FONT_FAMILY, 9, "bold"),
            text_color=TEXT_DIM,
            fg_color="rgba(255,255,255,0.05)",
            corner_radius=6,
            height=20,
            width=30
        )
        esc_hint.pack(side="right")
        
        # Separator
        ctk.CTkFrame(self.container, fg_color="rgba(255,255,255,0.05)", height=1).pack(fill="x")
        
        # Command List (Scrollable)
        self.list_frame = ctk.CTkScrollableFrame(
            self.container, 
            fg_color="transparent",
            corner_radius=0
        )
        self.list_frame.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Footer
        ctk.CTkFrame(self.container, fg_color="rgba(255,255,255,0.05)", height=1).pack(fill="x")
        ctk.CTkLabel(
            self.container,
            text="ALT + SPACE to toggle",
            font=(FONT_FAMILY, 9, "bold"),
            text_color="#27272a"
        ).pack(pady=8)
        
        # Keybindings
        self.bind("<Escape>", lambda e: self.hide())
        self.bind("<Return>", self._on_enter)
        self.bind("<Down>", self._on_down)
        self.bind("<Up>", self._on_up)
        
        # State
        self._filtered_commands = COMMANDS.copy()
        self._selected_index = 0
        self._command_widgets = []
        
        self.withdraw() # Hide initially
        self._render_commands()

    def _on_search_change(self, *args):
        query = self.search_var.get().strip().lower()
        if query:
            self._filtered_commands = [c for c in COMMANDS if query in c['label'].lower() or query in c['category'].lower()]
        else:
            self._filtered_commands = COMMANDS.copy()
        
        self._selected_index = 0
        self._render_commands()

    def _render_commands(self):
        # Clear existing
        for widget in self._command_widgets:
            widget.destroy()
        self._command_widgets.clear()
        
        if not self._filtered_commands:
            lbl = ctk.CTkLabel(
                self.list_frame, 
                text="NO MATCHING COMMANDS",
                font=(FONT_FAMILY, 11, "bold"),
                text_color=TEXT_DIM
            )
            lbl.pack(pady=24)
            self._command_widgets.append(lbl)
            return

        for i, cmd in enumerate(self._filtered_commands):
            is_selected = (i == self._selected_index)
            bg_color = HOVER_BG if is_selected else "transparent"
            
            btn = ctk.CTkFrame(
                self.list_frame, 
                fg_color=bg_color,
                corner_radius=12,
                cursor="hand2"
            )
            btn.pack(fill="x", pady=2)
            
            # Click event mapping
            def make_cmd(action):
                return lambda e: self._execute(action)
            
            # Label
            lbl = ctk.CTkLabel(
                btn, 
                text=cmd["label"],
                font=(FONT_FAMILY, 12),
                text_color=TEXT_PRIMARY if is_selected else TEXT_MUTED,
                anchor="w"
            )
            lbl.pack(side="left", padx=(14, 10), pady=10)
            
            # Category
            cat = ctk.CTkLabel(
                btn,
                text=cmd["category"].upper(),
                font=(FONT_FAMILY, 9, "bold"),
                text_color=TEXT_DIM,
                anchor="e"
            )
            cat.pack(side="right", padx=14, pady=10)
            
            # Bind clicks
            lbl.bind("<Button-1>", make_cmd(cmd["action"]))
            cat.bind("<Button-1>", make_cmd(cmd["action"]))
            btn.bind("<Button-1>", make_cmd(cmd["action"]))
            
            self._command_widgets.append(btn)

    def _on_up(self, event):
        if not self._filtered_commands: return
        self._selected_index = max(0, self._selected_index - 1)
        self._render_commands()
        return "break"

    def _on_down(self, event):
        if not self._filtered_commands: return
        self._selected_index = min(len(self._filtered_commands) - 1, self._selected_index + 1)
        self._render_commands()
        return "break"

    def _on_enter(self, event):
        if not self._filtered_commands: return
        cmd = self._filtered_commands[self._selected_index]
        self._execute(cmd["action"])

    def _execute(self, action):
        self.hide()
        if self.on_command_callback:
            self.on_command_callback(action)

    def toggle(self):
        if self.winfo_viewable():
            self.hide()
        else:
            self.show()

    def show(self):
        self.search_var.set("")
        self._selected_index = 0
        self._render_commands()
        self.deiconify()
        self.lift()
        self.focus_force()
        self.search_entry.focus()

    def hide(self):
        self.withdraw()
