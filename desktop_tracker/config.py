"""
LifeOS Desktop Tracker — Configuration
All tunable parameters live here.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── API ──────────────────────────────────────────────────────
API_BASE_URL: str = os.getenv("LIFEOS_API_URL", "http://localhost:8000")
LIFEOS_EMAIL: str = os.getenv("LIFEOS_EMAIL", "")
LIFEOS_PASSWORD: str = os.getenv("LIFEOS_PASSWORD", "")

# ── Polling ──────────────────────────────────────────────────
POLL_INTERVAL_SECONDS: int = 5          # How often to sample the active window
FLUSH_INTERVAL_POLLS: int = 6          # Flush to API every N polls (= 30 sec default)

# ── Idle Detection ───────────────────────────────────────────
IDLE_THRESHOLD_SECONDS: int = 300      # 5 minutes — pause tracking beyond this

# ── Session Aggregation ──────────────────────────────────────
# Consecutive polls on the same (app + title) are merged into one session.
# A new session starts when app or title changes.
MIN_SESSION_SECONDS: int = 5           # Discard micro-sessions below this threshold
