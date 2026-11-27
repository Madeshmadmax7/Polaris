"""
LifeOS Desktop Agent — App Blocker
Terminates blocked/distracting applications and shows a Windows toast notification.

Blocking sources:
  1. Parental blocked list (synced from backend)
  2. Focus mode: auto-block all apps classified as 'distracting'

Uses psutil to kill processes and winotify for native Windows toasts.
"""

import logging
import threading
import time
from typing import Optional

import psutil
from winotify import Notification, audio

from classifier import DISTRACTING_APPS
from block_overlay import show_block_overlay

logger = logging.getLogger(__name__)

# How often to re-fetch the blocked list from backend (seconds)
BLOCKED_LIST_REFRESH_INTERVAL = 60


class AppBlocker:
    """
    Monitors and blocks restricted desktop applications.

    Usage:
        blocker = AppBlocker(api_client=client)
        blocker.start_sync()          # Start background sync of blocked list
        blocker.check_and_block(snap)  # Called each poll cycle from tracker
    """

    def __init__(self, api_client=None):
        self._api_client = api_client
        self._blocked_apps: set[str] = set()   # e.g. {"valorant.exe", "discord.exe"}
        self._focus_mode: bool = False
        self._distraction_blocker_enabled: bool = True  # Distraction blocker active by default
        self._sync_thread: Optional[threading.Thread] = None
        self._running = True

        # Track recently blocked to avoid spamming notifications
        self._recently_blocked: dict[str, float] = {}
        self._cooldown_seconds = 30  # Don't re-notify for same app within 30s

    # ── Public API ───────────────────────────────────────────

    @property
    def focus_mode(self) -> bool:
        return self._focus_mode

    @focus_mode.setter
    def focus_mode(self, enabled: bool):
        self._focus_mode = enabled
        logger.info("Focus mode %s", "ENABLED" if enabled else "DISABLED")

    @property
    def distraction_blocker_enabled(self) -> bool:
        return self._distraction_blocker_enabled

    @distraction_blocker_enabled.setter
    def distraction_blocker_enabled(self, enabled: bool):
        self._distraction_blocker_enabled = enabled
        logger.info("Distraction blocker %s", "ENABLED" if enabled else "DISABLED")

    @property
    def blocked_count(self) -> int:
        return len(self._blocked_apps)

    def add_blocked_app(self, exe_name: str):
        """Manually add an app to the local blocked list."""
        if exe_name and exe_name.strip():
            name = exe_name.strip().lower()
            if not name.endswith(".exe"):
                name += ".exe"
            self._blocked_apps.add(name)
            logger.info("Added to blocklist: %s", name)

    def remove_blocked_app(self, exe_name: str):
        """Remove an app from the local blocked list."""
        name = exe_name.strip().lower()
        self._blocked_apps.discard(name)
        if not name.endswith(".exe"):
            self._blocked_apps.discard(name + ".exe")
        logger.info("Removed from blocklist: %s", name)

    def get_blocked_list(self) -> list[str]:
        """Return the current blocked app list."""
        return sorted(self._blocked_apps)

    def check_and_block(self, exe_name: str, app_name: str, category: str, pid: int) -> bool:
        """
        Check if the given app should be blocked. If so, kill it and notify.

        Args:
            exe_name:  Raw process name, e.g. "valorant.exe"
            app_name:  Friendly name, e.g. "Valorant"
            category:  Classification: "productive" | "distracting" | "neutral"
            pid:       Process ID

        Returns:
            True if the app was blocked (killed), False otherwise.
        """
        normalized = exe_name.strip().lower()

        should_block = False
        reason = ""

        # Check 1: Is the app in the explicit blocked list?
        if normalized in self._blocked_apps or exe_name.lower() in self._blocked_apps:
            should_block = True
            reason = f"{app_name} is in your blocked applications list."

        # Check 2: Distraction blocker or Focus mode — block all distracting apps
        elif (self._focus_mode or self._distraction_blocker_enabled) and (category == "distracting" or normalized in DISTRACTING_APPS):
            should_block = True
            reason = f"{app_name} is classified as distracting and has been blocked."

        if not should_block:
            return False

        # Cooldown check — don't spam notifications
        now = time.time()
        last_blocked = self._recently_blocked.get(normalized, 0)
        if now - last_blocked < self._cooldown_seconds:
            # Still kill it, but don't show notification again
            self._kill_process(pid, app_name)
            return True

        self._recently_blocked[normalized] = now

        # Show fullscreen block overlay (like Chrome extension)
        show_block_overlay(app_name, reason, auto_dismiss_seconds=5)

        # Kill the process
        self._kill_process(pid, app_name)

        # Show Windows toast notification
        self._show_block_notification(app_name, reason)

        logger.info("BLOCKED: %s (PID %d) — %s", app_name, pid, reason)
        return True

    # ── Background Sync ──────────────────────────────────────

    def start_sync(self):
        """Start background thread to periodically sync blocked list from backend."""
        self._running = True
        self._sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self._sync_thread.start()
        logger.info("App blocker sync started.")

    def stop_sync(self):
        """Stop the background sync thread."""
        self._running = False

    def _sync_loop(self):
        """Periodically fetch the blocked app list from the backend."""
        while self._running:
            try:
                self._fetch_blocked_list()
            except Exception as e:
                logger.error("Failed to sync blocked list: %s", e)
            time.sleep(BLOCKED_LIST_REFRESH_INTERVAL)

    def _fetch_blocked_list(self):
        """Fetch blocked apps/sites from the backend API."""
        if not self._api_client:
            return

        try:
            blocked, focus_mode = self._api_client.get_blocked_apps()
            self._focus_mode = focus_mode
            if blocked is not None:
                # Merge with any locally-added blocks
                for app in blocked:
                    self._blocked_apps.add(app.strip().lower())
                logger.debug("Synced %d blocked apps from backend.", len(blocked))
        except Exception as e:
            logger.debug("Blocked list sync error: %s", e)

    # ── Process Killing ──────────────────────────────────────

    @staticmethod
    def _kill_process(pid: int, app_name: str):
        """Forcefully terminate a process by PID."""
        try:
            proc = psutil.Process(pid)
            proc.kill()
            logger.info("Killed process: %s (PID %d)", app_name, pid)
        except psutil.NoSuchProcess:
            pass  # Already gone
        except psutil.AccessDenied:
            logger.warning("Access denied killing %s (PID %d). Run as admin.", app_name, pid)
        except Exception as e:
            logger.error("Error killing %s: %s", app_name, e)

    # ── Windows Toast Notification ───────────────────────────

    @staticmethod
    def _show_block_notification(app_name: str, reason: str):
        """Show a native Windows toast notification."""
        try:
            toast = Notification(
                app_id="LifeOS Desktop Agent",
                title=f"🚫 {app_name} Blocked",
                msg=reason,
                duration="short",
            )
            toast.set_audio(audio.Default, loop=False)
            toast.show()
        except Exception as e:
            logger.debug("Toast notification failed: %s", e)
