"""
LifeOS Desktop Agent — System Tray Icon
Provides a persistent system tray icon with right-click context menu.
Uses pystray + Pillow for cross-platform tray management.
"""

import logging
import threading
from typing import Callable, Optional

from PIL import Image, ImageDraw, ImageFont
import pystray

logger = logging.getLogger(__name__)


def _create_icon_image(size: int = 64, status: str = "active") -> Image.Image:
    """
    Generate a LifeOS tray icon programmatically.
    Green dot = active, Yellow = paused, Red = disconnected.
    """
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Outer circle — dark background
    draw.ellipse([2, 2, size - 2, size - 2], fill=(15, 15, 25, 255))

    # Inner ring — status color
    colors = {
        "active": (34, 197, 94),     # green-500
        "paused": (250, 204, 21),    # yellow-400
        "error": (239, 68, 68),      # red-500
    }
    color = colors.get(status, colors["active"])

    # Draw a "L" stylized letter for LifeOS
    ring_margin = size // 6
    draw.ellipse(
        [ring_margin, ring_margin, size - ring_margin, size - ring_margin],
        outline=color, width=3,
    )

    # Status dot in bottom-right
    dot_r = size // 8
    dot_x = size - dot_r * 2 - 2
    dot_y = size - dot_r * 2 - 2
    draw.ellipse([dot_x, dot_y, dot_x + dot_r * 2, dot_y + dot_r * 2], fill=color)

    return img


class SystemTray:
    """
    Manages the LifeOS system tray icon and its context menu.

    Usage:
        tray = SystemTray(
            on_open=lambda: ...,
            on_pause=lambda: ...,
            on_resume=lambda: ...,
            on_quit=lambda: ...,
        )
        tray.start()      # Runs in background thread
        tray.update_status("paused")
        tray.stop()
    """

    def __init__(
        self,
        on_open: Optional[Callable] = None,
        on_pause: Optional[Callable] = None,
        on_resume: Optional[Callable] = None,
        on_quit: Optional[Callable] = None,
    ):
        self._on_open = on_open or (lambda: None)
        self._on_pause = on_pause or (lambda: None)
        self._on_resume = on_resume or (lambda: None)
        self._on_quit = on_quit or (lambda: None)
        self._icon: Optional[pystray.Icon] = None
        self._thread: Optional[threading.Thread] = None
        self._status = "active"

    def _build_menu(self) -> pystray.Menu:
        """Build the right-click context menu."""
        return pystray.Menu(
            pystray.MenuItem("Open LifeOS Dashboard", self._handle_open, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Pause Tracking", self._handle_pause),
            pystray.MenuItem("Resume Tracking", self._handle_resume),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._handle_quit),
        )

    def _handle_open(self, icon, item):
        self._on_open()

    def _handle_pause(self, icon, item):
        self._status = "paused"
        self._on_pause()
        self._refresh_icon()

    def _handle_resume(self, icon, item):
        self._status = "active"
        self._on_resume()
        self._refresh_icon()

    def _handle_quit(self, icon, item):
        self._on_quit()
        self.stop()

    def _refresh_icon(self):
        """Update the tray icon to reflect current status."""
        if self._icon:
            self._icon.icon = _create_icon_image(status=self._status)

    def update_status(self, status: str):
        """Update tray icon status: 'active', 'paused', or 'error'."""
        self._status = status
        self._refresh_icon()

    def start(self):
        """Start the system tray icon in a background thread."""
        self._icon = pystray.Icon(
            name="LifeOS",
            icon=_create_icon_image(status=self._status),
            title="LifeOS Desktop Tracker",
            menu=self._build_menu(),
        )
        self._thread = threading.Thread(target=self._icon.run, daemon=True)
        self._thread.start()
        logger.info("System tray icon started.")

    def stop(self):
        """Stop and remove the system tray icon."""
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass
        logger.info("System tray icon stopped.")
