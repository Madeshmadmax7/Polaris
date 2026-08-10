"""
LifeOS Desktop Tracker — Main Polling Loop
Windows only. Requires: pywin32, psutil, requests, python-dotenv

How it works:
  1. Every POLL_INTERVAL_SECONDS, sample the foreground window.
  2. Resolve the EXE → friendly name, classify it, read window title.
  3. Check Windows idle time via GetLastInputInfo.
  4. Accumulate time into the current "session" (same app + title = same session).
  5. When the app/title changes OR after FLUSH_INTERVAL_POLLS, flush to backend.
"""

import ctypes
import ctypes.wintypes
import logging
import os
import signal
import sys
import time
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

import psutil
import win32gui
import win32process

from api_client import LifeOSClient
from app_resolver import resolve as resolve_app_name
from classifier import classify, is_browser
from config import (
    FLUSH_INTERVAL_POLLS,
    IDLE_THRESHOLD_SECONDS,
    MIN_SESSION_SECONDS,
    POLL_INTERVAL_SECONDS,
)

# ── Logging Setup ────────────────────────────────────────────────────────────
def _setup_logging():
    log_handlers = [logging.StreamHandler(sys.stdout)]
    try:
        local_appdata = os.getenv("LOCALAPPDATA") or os.path.expanduser("~")
        log_dir = os.path.join(local_appdata, "POLARIS")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "desktop_tracker.log")
        log_handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    except Exception:
        pass  # Fallback to stdout only if file handler cannot be created

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        handlers=log_handlers,
    )

_setup_logging()
logger = logging.getLogger(__name__)


# ── Windows Idle Time via ctypes ─────────────────────────────────────────────

class _LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("dwTime", ctypes.c_ulong),
    ]


def get_idle_seconds() -> float:
    """
    Return the number of seconds since the user last moved the mouse or
    pressed a key, using the Windows GetLastInputInfo API.
    Requires no external libraries — ctypes is part of the Python stdlib.
    """
    lii = _LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(_LASTINPUTINFO)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
    millis_elapsed = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
    return millis_elapsed / 1000.0


# ── Active Window Detection ──────────────────────────────────────────────────

@dataclass
class WindowSnapshot:
    """A point-in-time snapshot of the active window."""
    exe:         str           # Raw process name, e.g. "code.exe"
    application: str           # Friendly name, e.g. "Visual Studio Code"
    window_title: str          # Full window title, e.g. "Polaris — App.jsx"
    category:    str           # "productive" | "distracting" | "neutral"
    is_browser:  bool          # True → Chrome extension handles it


def get_active_window() -> Optional[WindowSnapshot]:
    """
    Return a WindowSnapshot of the currently focused desktop window,
    or None if detection fails or the system is at the desktop.
    """
    try:
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            return None

        window_title = win32gui.GetWindowText(hwnd).strip()

        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        proc = psutil.Process(pid)
        exe_name = proc.name()                      # e.g. "Code.exe"

        app_name = resolve_app_name(exe_name)       # "Visual Studio Code"
        category = classify(exe_name, window_title)
        browser = is_browser(exe_name)

        return WindowSnapshot(
            exe=exe_name,
            application=app_name,
            window_title=window_title,
            category=category,
            is_browser=browser,
        )
    except (psutil.NoSuchProcess, psutil.AccessDenied, Exception):
        return None


# ── Session Accumulation ─────────────────────────────────────────────────────

@dataclass
class Session:
    """An ongoing or completed block of time spent in one app + window title."""
    application:  str
    process:      str
    window_title: str
    category:     str
    started_at:   datetime
    duration_seconds: int = 0
    active_seconds:   int = 0      # Excludes idle time
    is_active:    bool = True      # False once predominantly idle


def session_key(snap: WindowSnapshot) -> str:
    """Sessions are keyed by (app name, window title)."""
    return f"{snap.application}::{snap.window_title}"


# ── Graceful Shutdown ────────────────────────────────────────────────────────

_running = True


def _handle_shutdown(signum, frame):
    global _running
    logger.info("Shutdown signal received. Flushing remaining sessions...")
    _running = False


signal.signal(signal.SIGINT, _handle_shutdown)
signal.signal(signal.SIGTERM, _handle_shutdown)


# ── Tracking Engine (Thread-safe wrapper) ────────────────────────────────────

class TrackingEngine:
    """
    Wraps the polling loop in a background thread for GUI integration.

    Usage:
        engine = TrackingEngine(client)
        engine.start()         # Non-blocking
        engine.pause()
        engine.resume()
        engine.get_status()    # Dict with current app, category, duration
        engine.stop()
    """

    def __init__(self, client: LifeOSClient, blocker=None):
        self._client = client
        self._blocker = blocker
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._paused = False

        # Live status for GUI
        self._current_app: str = ""
        self._current_category: str = ""
        self._current_title: str = ""
        self._session_duration: int = 0
        self._total_productive: int = 0
        self._total_distracting: int = 0
        self._total_neutral: int = 0
        self._apps_blocked: int = 0

    # ── Public API ───────────────────────────────────────────

    def start(self):
        """Start tracking in a background thread."""
        if self._thread and self._thread.is_alive():
            return
        self._running = True
        self._paused = False
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("Tracking engine started in background thread.")

    def stop(self):
        """Stop the tracking loop."""
        self._running = False

    def pause(self):
        """Pause tracking (loop continues but skips data collection)."""
        self._paused = True
        logger.info("Tracking paused.")

    def resume(self):
        """Resume tracking."""
        self._paused = False
        logger.info("Tracking resumed.")

    @property
    def is_running(self) -> bool:
        return self._running and (self._thread is not None and self._thread.is_alive())

    @property
    def is_paused(self) -> bool:
        return self._paused

    def get_status(self) -> dict:
        """Return current tracking status for the GUI dashboard."""
        return {
            "app": self._current_app,
            "category": self._current_category,
            "title": self._current_title,
            "session_seconds": self._session_duration,
            "total_productive": self._total_productive,
            "total_distracting": self._total_distracting,
            "total_neutral": self._total_neutral,
            "apps_blocked": self._apps_blocked,
            "is_running": self.is_running,
            "is_paused": self._paused,
        }

    # ── Core Loop ────────────────────────────────────────────

    def _run_loop(self):
        """The main polling loop — runs in a background thread."""
        logger.info("=" * 60)
        logger.info("LifeOS Desktop Tracker starting...")
        logger.info("Poll interval : %ds", POLL_INTERVAL_SECONDS)
        logger.info("Idle threshold: %ds (%d min)", IDLE_THRESHOLD_SECONDS, IDLE_THRESHOLD_SECONDS // 60)
        logger.info("Flush interval: every %d polls (%ds)", FLUSH_INTERVAL_POLLS, FLUSH_INTERVAL_POLLS * POLL_INTERVAL_SECONDS)
        logger.info("=" * 60)

        # State
        current_session: Optional[Session] = None
        current_key: Optional[str] = None
        completed_sessions: list[dict] = []
        poll_count: int = 0

        while self._running:
            poll_count += 1

            # If paused, just sleep and continue
            if self._paused:
                time.sleep(POLL_INTERVAL_SECONDS)
                continue

            idle_seconds = get_idle_seconds()
            user_is_idle = idle_seconds >= IDLE_THRESHOLD_SECONDS
            snap = get_active_window()

            # NLP classification for unknown apps
            if snap and not snap.is_browser and snap.category == "unknown":
                logger.info("Unknown app '%s' detected, querying AI for classification...", snap.application)
                resolved_cat = self._client.classify_app(snap.application, snap.window_title)
                from classifier import dynamic_cache
                dynamic_cache[snap.exe] = resolved_cat
                snap.category = resolved_cat

            # ── Blocker check ──
            if snap and not snap.is_browser and self._blocker:
                try:
                    _, pid = win32process.GetWindowThreadProcessId(
                        win32gui.GetForegroundWindow()
                    )
                    was_blocked = self._blocker.check_and_block(
                        exe_name=snap.exe,
                        app_name=snap.application,
                        category=snap.category,
                        pid=pid,
                    )
                    if was_blocked:
                        self._apps_blocked += 1
                        snap = None  # Skip tracking this poll
                except Exception:
                    pass

            # Update live status for GUI
            if snap and not snap.is_browser:
                self._current_app = snap.application
                self._current_category = snap.category
                self._current_title = snap.window_title

            if snap is None or snap.is_browser:
                if snap and snap.is_browser:
                    logger.debug("Skipping browser: %s", snap.application)
            elif user_is_idle:
                if current_session:
                    logger.info(
                        "Idle detected (%.0fs). Pausing session: %s",
                        idle_seconds, current_session.application,
                    )
                    completed_sessions.append({
                        "application":    current_session.application,
                        "process":        current_session.process,
                        "window_title":   current_session.window_title,
                        "category":       current_session.category,
                        "duration_seconds": int(idle_seconds),
                        "is_active":      False,
                        "timestamp":      datetime.now(timezone.utc),
                    })
                    current_session = None
                    current_key = None
            else:
                key = session_key(snap)

                if key != current_key:
                    if current_session and current_session.duration_seconds >= MIN_SESSION_SECONDS:
                        completed_sessions.append({
                            "application":    current_session.application,
                            "process":        current_session.process,
                            "window_title":   current_session.window_title,
                            "category":       current_session.category,
                            "duration_seconds": current_session.duration_seconds,
                            "is_active":      True,
                            "timestamp":      current_session.started_at,
                        })
                        # Update stats
                        self._update_stats(current_session.category, current_session.duration_seconds)
                        logger.info(
                            "Session complete: [%s] %s -- %s | %ds",
                            current_session.category.upper(),
                            current_session.application,
                            current_session.window_title[:60],
                            current_session.duration_seconds,
                        )

                    current_session = Session(
                        application=snap.application,
                        process=snap.exe,
                        window_title=snap.window_title,
                        category=snap.category,
                        started_at=datetime.now(timezone.utc),
                        duration_seconds=POLL_INTERVAL_SECONDS,
                    )
                    current_key = key
                    self._session_duration = POLL_INTERVAL_SECONDS
                    logger.info(
                        "Now tracking: [%s] %s -- %s",
                        snap.category.upper(),
                        snap.application,
                        snap.window_title[:70],
                    )
                else:
                    current_session.duration_seconds += POLL_INTERVAL_SECONDS
                    self._session_duration = current_session.duration_seconds

            # Flush to backend
            if poll_count % FLUSH_INTERVAL_POLLS == 0:
                flush_list = list(completed_sessions)
                if current_session and current_session.duration_seconds >= MIN_SESSION_SECONDS:
                    flush_list.append({
                        "application":    current_session.application,
                        "process":        current_session.process,
                        "window_title":   current_session.window_title,
                        "category":       current_session.category,
                        "duration_seconds": current_session.duration_seconds,
                        "is_active":      True,
                        "timestamp":      current_session.started_at,
                    })
                    current_session.started_at = datetime.now(timezone.utc)
                    current_session.duration_seconds = 0

                if flush_list:
                    self._client.flush_batch(flush_list)
                completed_sessions.clear()

            time.sleep(POLL_INTERVAL_SECONDS)

        # Shutdown flush
        if current_session and current_session.duration_seconds >= MIN_SESSION_SECONDS:
            completed_sessions.append({
                "application":    current_session.application,
                "process":        current_session.process,
                "window_title":   current_session.window_title,
                "category":       current_session.category,
                "duration_seconds": current_session.duration_seconds,
                "is_active":      True,
                "timestamp":      current_session.started_at,
            })

        if completed_sessions:
            logger.info("Flushing %d remaining sessions before exit...", len(completed_sessions))
            self._client.flush_batch(completed_sessions)

        logger.info("Desktop Tracker stopped cleanly.")

    def _update_stats(self, category: str, seconds: int):
        """Accumulate time stats by category."""
        if category == "productive":
            self._total_productive += seconds
        elif category == "distracting":
            self._total_distracting += seconds
        else:
            self._total_neutral += seconds


# ── CLI Entry Point (backwards compatible) ───────────────────────────────────

def main():
    """Original CLI entry point — authenticate and run the tracking loop."""
    client = LifeOSClient()
    if not client.authenticate():
        logger.error("Cannot start: authentication failed. Check your .env credentials.")
        sys.exit(1)

    from blocker import AppBlocker
    blocker = AppBlocker(api_client=client)
    blocker.start_sync()

    engine = TrackingEngine(client, blocker=blocker)
    engine.start()

    # Block the main thread until shutdown signal
    try:
        while engine.is_running:
            time.sleep(1)
    except KeyboardInterrupt:
        engine.stop()


if __name__ == "__main__":
    main()

