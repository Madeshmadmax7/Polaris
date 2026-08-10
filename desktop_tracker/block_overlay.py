"""
LifeOS Desktop Agent — Block Overlay
Full-screen dark overlay that appears when a distracting app is detected.
Matches the Chrome extension's block overlay design.

Uses CTkToplevel so it runs safely on the main GUI thread.
The blocker calls a callback which schedules overlay creation via .after().
"""

import logging
import tkinter as tk
from tkinter import font as tkfont

import customtkinter as ctk

logger = logging.getLogger(__name__)

# ── Design Tokens ────────────────────────────────────────────────
BG_COLOR       = "#0a0a1a"
TEXT_PRIMARY   = "#ffffff"
TEXT_MUTED_HEX = "#999999"
BUTTON_BG      = "#ffffff"
BUTTON_FG      = "#000000"
BUTTON_HOVER   = "#e0e0e0"


class BlockOverlayWindow(ctk.CTkToplevel):
    """
    Full-screen blocking overlay window.
    Must be created from the main thread via root.after().
    """

    def __init__(self, master, app_name: str, reason: str,
                 auto_dismiss_seconds: int = 5):
        super().__init__(master)

        self.title("POLARIS — Focus Mode")
        self.configure(fg_color=BG_COLOR)
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        # Full screen
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{sw}x{sh}+0+0")

        # Prevent closing
        self.protocol("WM_DELETE_WINDOW", lambda: None)

        # ── Background Canvas ──
        canvas = tk.Canvas(self, width=sw, height=sh, bg=BG_COLOR,
                           highlightthickness=0, bd=0)
        canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # Radial gradient circles
        cx, cy = sw // 2, sh // 2
        for i in range(40, 0, -1):
            radius = i * 12
            r = 10 + int(i * 0.3)
            g = 10 + int(i * 0.3)
            b = 26 + int(i * 1.2)
            color = f"#{min(r, 255):02x}{min(g, 255):02x}{min(b, 255):02x}"
            canvas.create_oval(
                cx - radius, cy - radius,
                cx + radius, cy + radius,
                fill=color, outline="",
            )

        # ── Central Card ──
        card_w, card_h = 620, 420
        card_x = cx - card_w // 2
        card_y = cy - card_h // 2

        _draw_rounded_rect(canvas, card_x, card_y,
                           card_x + card_w, card_y + card_h,
                           radius=40, fill="#111122", outline="#2a2a4a")

        # ── Shield Icon ──
        _draw_shield(canvas, cx, card_y + 70, size=50, color="#ffffff")

        # ── Heading ──
        try:
            h_font = tkfont.Font(family="Segoe UI", size=28, weight="bold")
        except Exception:
            h_font = tkfont.Font(size=28, weight="bold")
        canvas.create_text(cx, card_y + 140,
                           text="Focus Mode Active",
                           fill=TEXT_PRIMARY, font=h_font)

        # ── Subtext ──
        try:
            s_font = tkfont.Font(family="Segoe UI", size=14)
        except Exception:
            s_font = tkfont.Font(size=14)
        canvas.create_text(cx, card_y + 195,
                           text=f"{app_name} is classified as distracting.",
                           fill=TEXT_MUTED_HEX, font=s_font)
        canvas.create_text(cx, card_y + 225,
                           text="Redirect your energy towards your goals.",
                           fill=TEXT_MUTED_HEX, font=s_font)

        # ── Button ──
        btn_w, btn_h = 280, 56
        btn_x = cx - btn_w // 2
        btn_y = card_y + 280

        btn_items = _draw_rounded_rect(
            canvas, btn_x, btn_y, btn_x + btn_w, btn_y + btn_h,
            radius=28, fill=BUTTON_BG, outline="")

        try:
            b_font = tkfont.Font(family="Segoe UI", size=13, weight="bold")
        except Exception:
            b_font = tkfont.Font(size=13, weight="bold")

        btn_text = canvas.create_text(
            cx, btn_y + btn_h // 2,
            text="GO BACK TO WORK",
            fill=BUTTON_FG, font=b_font)

        # Button interactions
        def _hover(e):
            for item in btn_items:
                canvas.itemconfig(item, fill=BUTTON_HOVER)

        def _leave(e):
            for item in btn_items:
                canvas.itemconfig(item, fill=BUTTON_BG)

        def _click(e):
            self._close()

        for item_id in btn_items + [btn_text]:
            canvas.tag_bind(item_id, "<Enter>", _hover)
            canvas.tag_bind(item_id, "<Leave>", _leave)
            canvas.tag_bind(item_id, "<Button-1>", _click)

        # ── Countdown ──
        if auto_dismiss_seconds > 0:
            try:
                t_font = tkfont.Font(family="Segoe UI", size=10)
            except Exception:
                t_font = tkfont.Font(size=10)

            self._countdown_id = canvas.create_text(
                cx, card_y + card_h - 30,
                text=f"Auto-closing in {auto_dismiss_seconds}s",
                fill="#555577", font=t_font)
            self._canvas = canvas
            self._remaining = auto_dismiss_seconds
            self.after(1000, self._tick_countdown)

        # ── Branding ──
        try:
            br_font = tkfont.Font(family="Segoe UI", size=8, weight="bold")
        except Exception:
            br_font = tkfont.Font(size=8, weight="bold")
        canvas.create_text(cx, sh - 40,
                           text="POLARIS DESKTOP AGENT",
                           fill="#333355", font=br_font)

        # Keyboard
        self.bind("<Escape>", lambda e: self._close())
        self.bind("<Alt-F4>", lambda e: "break")

        self.focus_force()
        self.lift()

    def _tick_countdown(self):
        """Countdown timer tick."""
        self._remaining -= 1
        if self._remaining <= 0:
            self._close()
            return
        try:
            self._canvas.itemconfig(
                self._countdown_id,
                text=f"Auto-closing in {self._remaining}s")
            self.after(1000, self._tick_countdown)
        except Exception:
            pass

    def _close(self):
        """Safely destroy the overlay."""
        try:
            self.destroy()
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════
#  OVERLAY MANAGER — Thread-safe bridge
# ══════════════════════════════════════════════════════════════

_app_root = None  # Set by gui_app.py on startup


def set_app_root(root):
    """Called by gui_app.py to register the main Tk root for overlay creation."""
    global _app_root
    _app_root = root


def show_block_overlay(app_name: str, reason: str,
                       auto_dismiss_seconds: int = 5):
    """
    Thread-safe: schedules overlay creation on the main Tk thread.
    Called from the blocker's background thread.
    """
    root = _app_root
    if root is None:
        logger.warning("No app root set — cannot show overlay.")
        return

    try:
        root.after(0, lambda: BlockOverlayWindow(
            root, app_name, reason, auto_dismiss_seconds))
    except Exception as e:
        logger.debug("Could not show overlay: %s", e)


def dismiss_block_overlay():
    """Placeholder for programmatic dismiss (overlay auto-closes)."""
    pass


# ══════════════════════════════════════════════════════════════
#  CANVAS DRAWING HELPERS
# ══════════════════════════════════════════════════════════════

def _draw_rounded_rect(canvas, x1, y1, x2, y2, radius=20,
                       fill="#000", outline="#333", width=1):
    """Draw a rounded rectangle on a Tk Canvas."""
    items = []
    r = radius

    items.append(canvas.create_rectangle(
        x1 + r, y1, x2 - r, y2, fill=fill, outline="", width=0))
    items.append(canvas.create_rectangle(
        x1, y1 + r, x2, y2 - r, fill=fill, outline="", width=0))

    items.append(canvas.create_oval(
        x1, y1, x1 + 2 * r, y1 + 2 * r, fill=fill, outline="", width=0))
    items.append(canvas.create_oval(
        x2 - 2 * r, y1, x2, y1 + 2 * r, fill=fill, outline="", width=0))
    items.append(canvas.create_oval(
        x1, y2 - 2 * r, x1 + 2 * r, y2, fill=fill, outline="", width=0))
    items.append(canvas.create_oval(
        x2 - 2 * r, y2 - 2 * r, x2, y2, fill=fill, outline="", width=0))

    if outline and width > 0:
        canvas.create_line(x1 + r, y1, x2 - r, y1, fill=outline, width=width)
        canvas.create_line(x1 + r, y2, x2 - r, y2, fill=outline, width=width)
        canvas.create_line(x1, y1 + r, x1, y2 - r, fill=outline, width=width)
        canvas.create_line(x2, y1 + r, x2, y2 - r, fill=outline, width=width)
        canvas.create_arc(x1, y1, x1 + 2 * r, y1 + 2 * r,
                          start=90, extent=90, style="arc",
                          outline=outline, width=width)
        canvas.create_arc(x2 - 2 * r, y1, x2, y1 + 2 * r,
                          start=0, extent=90, style="arc",
                          outline=outline, width=width)
        canvas.create_arc(x1, y2 - 2 * r, x1 + 2 * r, y2,
                          start=180, extent=90, style="arc",
                          outline=outline, width=width)
        canvas.create_arc(x2 - 2 * r, y2 - 2 * r, x2, y2,
                          start=270, extent=90, style="arc",
                          outline=outline, width=width)

    return items


def _draw_shield(canvas, cx, cy, size=50, color="#ffffff"):
    """Draw a shield icon at center (cx, cy)."""
    s = size / 24
    points = [
        cx, cy - 11 * s,
        cx + 8 * s, cy - 8 * s,
        cx + 8 * s, cy - 2 * s,
        cx + 6 * s, cy + 4 * s,
        cx + 3 * s, cy + 8 * s,
        cx, cy + 11 * s,
        cx - 3 * s, cy + 8 * s,
        cx - 6 * s, cy + 4 * s,
        cx - 8 * s, cy - 2 * s,
        cx - 8 * s, cy - 8 * s,
    ]
    canvas.create_polygon(points, fill="", outline=color,
                          width=2, smooth=True)
