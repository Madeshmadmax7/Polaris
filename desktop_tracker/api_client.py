"""
LifeOS Desktop Tracker — API Client
Handles authentication and batch log submission to the FastAPI backend.
Automatically re-authenticates if the token expires (HTTP 401).
"""

import base64
import json
import logging
import os
from datetime import datetime, timezone
from typing import Optional

import requests

from config import API_BASE_URL, LIFEOS_EMAIL, LIFEOS_PASSWORD

logger = logging.getLogger(__name__)

SESSION_FILE = os.path.join(os.path.expanduser("~"), ".lifeos_desktop_session.json")


class LifeOSClient:
    """
    Lightweight HTTP client for the LifeOS FastAPI backend.

    Usage:
        client = LifeOSClient()
        client.authenticate()
        client.flush_batch(sessions)
    """

    def __init__(self):
        self._token: Optional[str] = None
        self._user_info: dict = {}      # {"username": ..., "email": ...}
        self._user_id: Optional[str] = None
        self._session = requests.Session()
        self._session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "LifeOS-Desktop-Tracker/1.0",
        })
        self._load_session()

    def _load_session(self):
        """Load saved session token from disk if it exists."""
        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE, "r") as f:
                    data = json.load(f)
                    self._token = data.get("access_token")
                    self._user_info = data.get("user_info", {})
                    self._user_id = data.get("user_id")
                    if self._token:
                        self._session.headers.update({"Authorization": f"Bearer {self._token}"})
            except Exception as e:
                logger.error("Failed to load session: %s", e)

    def _save_session(self):
        """Save current session token to disk."""
        if self._token:
            try:
                with open(SESSION_FILE, "w") as f:
                    json.dump({
                        "access_token": self._token,
                        "user_info": self._user_info,
                        "user_id": self._user_id,
                    }, f)
            except Exception as e:
                logger.error("Failed to save session: %s", e)
                
    def logout(self):
        """Clear current session and delete saved session file."""
        self._token = None
        self._user_info = {}
        self._user_id = None
        if "Authorization" in self._session.headers:
            del self._session.headers["Authorization"]
        if os.path.exists(SESSION_FILE):
            try:
                os.remove(SESSION_FILE)
            except OSError:
                pass

    # ── Auth ─────────────────────────────────────────────────

    def authenticate(self) -> bool:
        """
        Login to the LifeOS backend and store the JWT token.
        Returns True on success, False on failure.
        """
        if not LIFEOS_EMAIL or not LIFEOS_PASSWORD:
            logger.error(
                "LIFEOS_EMAIL or LIFEOS_PASSWORD not set in .env. "
                "Copy .env.example to .env and fill in your credentials."
            )
            return False

        try:
            resp = self._session.post(
                f"{API_BASE_URL}/auth/login",
                json={"email": LIFEOS_EMAIL, "password": LIFEOS_PASSWORD},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            self._token = data.get("access_token")
            if not self._token:
                logger.error("Login succeeded but no access_token in response: %s", data)
                return False
            # Set on the session as a default header for all future requests
            self._session.headers.update({"Authorization": f"Bearer {self._token}"})
            self._user_info = data.get("user", {})
            self._user_id = self._extract_user_id()
            logger.info(
                "[OK] Authenticated as %s (%s)",
                self._user_info.get("username", "unknown"),
                self._user_info.get("email", ""),
            )
            logger.debug("Token prefix: %s...", self._token[:20])
            return True
        except requests.HTTPError as e:
            logger.error("Authentication failed: %s", e.response.text if e.response else e)
            return False
        except requests.RequestException as e:
            logger.error("Network error during authentication: %s", e)
            return False

    def _ensure_authenticated(self) -> bool:
        """Re-authenticate if we don't have a token yet."""
        if not self._token:
            return self.authenticate()
        return True

    # ── GUI-facing Methods ───────────────────────────────────

    def login_with_credentials(self, email: str, password: str) -> tuple[bool, str]:
        """
        Authenticate with explicit credentials (from GUI login form).
        Returns (success: bool, message: str).
        """
        try:
            resp = self._session.post(
                f"{API_BASE_URL}/auth/login",
                json={"email": email, "password": password},
                timeout=10,
            )
            if resp.status_code == 401:
                return False, "Invalid email or password."
            resp.raise_for_status()
            data = resp.json()
            self._token = data.get("access_token")
            if not self._token:
                return False, "Login succeeded but no token received."
            self._session.headers.update({"Authorization": f"Bearer {self._token}"})
            self._user_info = data.get("user", {})
            self._user_id = self._extract_user_id()
            self._save_session()
            return True, f"Welcome, {self._user_info.get('username', 'User')}!"
        except requests.ConnectionError:
            return False, "Cannot connect to LifeOS server. Is the backend running?"
        except requests.RequestException as e:
            return False, f"Login failed: {e}"

    def verify_session(self) -> bool:
        """
        Verify if the currently loaded session token is valid by pinging /auth/me.
        If valid, returns True. If invalid/expired, clears session and returns False.
        """
        if not self._token:
            return False
            
        try:
            resp = self._session.get(f"{API_BASE_URL}/auth/me", timeout=5)
            if resp.status_code == 200:
                self._user_info = resp.json()
                self._save_session()
                return True
            else:
                self.logout()
                return False
        except requests.RequestException:
            # If server is unreachable but we have a token, we could optionally allow offline usage.
            # But let's be strict or assume False if we can't verify.
            # Actually, to prevent breaking login when backend is briefly down,
            # we can return True if it's a connection error, but for safety, return False.
            # Let's return False so they have to login if offline (or if we can't reach the server).
            return False

    @property
    def user_info(self) -> dict:
        """Return user info dict: {username, email, ...}"""
        return self._user_info

    @property
    def user_id(self) -> Optional[str]:
        """Return the authenticated user's ID."""
        return self._user_id

    @property
    def is_authenticated(self) -> bool:
        return self._token is not None

    def _extract_user_id(self) -> Optional[str]:
        """Extract user_id from the JWT token payload."""
        if not self._token:
            return None
        try:
            payload_b64 = self._token.split(".")[1]
            # Fix padding
            payload_b64 += "=" * (4 - len(payload_b64) % 4)
            payload = json.loads(base64.b64decode(payload_b64))
            return payload.get("sub")
        except Exception as e:
            logger.error("Failed to extract user_id from token: %s", e)
            return None

    def get_blocked_apps(self) -> tuple[Optional[list[str]], bool]:
        """
        Fetch blocked apps and focus status for the current user from the backend.
        Returns (blocked_list, is_focus_mode), or (None, False) on failure.
        """
        if not self._ensure_authenticated() or not self._user_id:
            return None, False

        auth_headers = {"Authorization": f"Bearer {self._token}"}

        try:
            resp = self._session.get(
                f"{API_BASE_URL}/tracking/blocked-apps",
                headers=auth_headers,
                timeout=5,
            )
            if resp.status_code == 401:
                self._token = None
                if not self.authenticate():
                    return None
                auth_headers = {"Authorization": f"Bearer {self._token}"}
                resp = self._session.get(
                    f"{API_BASE_URL}/tracking/blocked-apps",
                    headers=auth_headers,
                    timeout=5,
                )
            resp.raise_for_status()
            data = resp.json()
            return data.get("blocked_apps", []), data.get("focus_mode_active", False)
        except Exception as e:
            logger.debug("Failed to fetch blocked apps: %s", e)
            return None, False

    def start_focus_session(self, duration_minutes: int) -> bool:
        """Start a focus session of given duration on the backend."""
        if not self._ensure_authenticated():
            return False

        auth_headers = {"Authorization": f"Bearer {self._token}"}
        payload = {"duration_minutes": duration_minutes}
        try:
            resp = self._session.post(
                f"{API_BASE_URL}/productivity/focus-session/start",
                json=payload,
                headers=auth_headers,
                timeout=10,
            )
            if resp.status_code == 401:
                self._token = None
                if not self.authenticate():
                    return False
                auth_headers = {"Authorization": f"Bearer {self._token}"}
                resp = self._session.post(
                    f"{API_BASE_URL}/productivity/focus-session/start",
                    json=payload,
                    headers=auth_headers,
                    timeout=10,
                )
            resp.raise_for_status()
            logger.info("Started focus session for %d minutes", duration_minutes)
            return True
        except Exception as e:
            logger.error("Failed to start focus session: %s", e)
            return False

    def stop_focus_session(self) -> bool:
        """Stop an active focus session on the backend."""
        if not self._ensure_authenticated():
            return False

        auth_headers = {"Authorization": f"Bearer {self._token}"}
        try:
            resp = self._session.post(
                f"{API_BASE_URL}/productivity/focus-session/stop",
                headers=auth_headers,
                timeout=10,
            )
            if resp.status_code == 401:
                self._token = None
                if not self.authenticate():
                    return False
                auth_headers = {"Authorization": f"Bearer {self._token}"}
                resp = self._session.post(
                    f"{API_BASE_URL}/productivity/focus-session/stop",
                    headers=auth_headers,
                    timeout=10,
                )
            resp.raise_for_status()
            logger.info("Stopped focus session")
            return True
        except Exception as e:
            logger.error("Failed to stop focus session: %s", e)
            return False

    # ── Batch Submission ─────────────────────────────────────

    def flush_batch(self, sessions: list[dict]) -> bool:
        """
        Submit a batch of completed desktop sessions to the backend.

        Each session dict must have:
          - application (str):    Friendly name, e.g. "Visual Studio Code"
          - process (str):        Raw EXE, e.g. "code.exe"
          - window_title (str):   Active window title
          - duration_seconds (int)
          - is_active (bool):     False if user was idle during this session
          - category (str):       "productive" | "distracting" | "neutral"
          - timestamp (datetime): UTC start time of the session

        Returns True if the batch was accepted, False otherwise.
        """
        if not sessions:
            return True

        if not self._ensure_authenticated():
            return False

        # Map internal session dicts to TrackingLogCreate schema
        logs = []
        for s in sessions:
            app_name = s.get("application", s.get("process", "Unknown"))
            domain = f"desktop://{app_name}"

            logs.append({
                "domain": domain,
                "page_title": s.get("window_title") or None,
                "duration_seconds": max(int(s.get("duration_seconds", 0)), 0),
                "tab_switches": 0,
                "scroll_depth": 0.0,
                "is_active": bool(s.get("is_active", True)),
                # yt_classification is repurposed to pre-classify desktop apps,
                # bypassing the backend's domain-based category lookup.
                "yt_classification": s.get("category", "neutral"),
                "timestamp": s["timestamp"].isoformat()
                if isinstance(s.get("timestamp"), datetime)
                else datetime.now(timezone.utc).isoformat(),
            })

        payload = {"logs": logs}

        # Explicitly inject token on every request — most reliable approach.
        # The session-level header is a fallback; this per-request header wins.
        auth_headers = {"Authorization": f"Bearer {self._token}"}

        logger.debug("Flushing %d sessions | token present: %s", len(logs), bool(self._token))

        try:
            resp = self._session.post(
                f"{API_BASE_URL}/tracking/batch",
                json=payload,
                headers=auth_headers,
                timeout=15,
            )

            # Token expired — re-authenticate and retry once
            if resp.status_code == 401:
                logger.warning("Token expired (401), re-authenticating...")
                self._token = None
                if not self.authenticate():
                    return False
                auth_headers = {"Authorization": f"Bearer {self._token}"}
                resp = self._session.post(
                    f"{API_BASE_URL}/tracking/batch",
                    json=payload,
                    headers=auth_headers,
                    timeout=15,
                )

            resp.raise_for_status()
            result = resp.json()
            ingested = result.get("ingested", 0)
            total = result.get("total", len(logs))
            logger.info("[OK] Flushed %d/%d desktop sessions to backend.", ingested, total)
            return True

        except requests.HTTPError as e:
            body = e.response.text if e.response else "(no body)"
            logger.error("Failed to flush batch: HTTP %s — %s", e.response.status_code if e.response else "?", body)
            return False
        except requests.RequestException as e:
            logger.error("Network error flushing batch: %s", e)
            return False

    def classify_app(self, app_name: str, window_title: str) -> str:
        """
        Dynamically classify an unknown application via the AI backend.
        Returns: "productive", "distracting", or "neutral"
        """
        if not self._ensure_authenticated():
            return "neutral"

        payload = {
            "app_name": app_name,
            "window_title": window_title
        }

        auth_headers = {"Authorization": f"Bearer {self._token}"}
        
        try:
            resp = self._session.post(
                f"{API_BASE_URL}/tracking/classify-app",
                json=payload,
                headers=auth_headers,
                timeout=5,
            )

            if resp.status_code == 401:
                self._token = None
                if not self.authenticate():
                    return "neutral"
                auth_headers = {"Authorization": f"Bearer {self._token}"}
                resp = self._session.post(
                    f"{API_BASE_URL}/tracking/classify-app",
                    json=payload,
                    headers=auth_headers,
                    timeout=5,
                )

            resp.raise_for_status()
            return resp.json().get("category", "neutral")
            
        except Exception as e:
            logger.error("Failed to dynamically classify app '%s': %s", app_name, e)
            return "neutral"
