# Polaris Tracker — HR-ready Project Overview

Polaris is a privacy-first activity tracker and parental-awareness dashboard designed to help families and learners understand device activity, focus patterns, and study progress. This repository contains the browser extension, backend API, and frontend dashboard used in the project.

Live demo: https://polaristracker.netlify.app

Table of contents
-----------------
- Project summary
- Product features
- Architecture & components
- Data flow
- Security & privacy
- Tech stack
- Deployment & hosting
- Local development (quick start)
- Project structure
- Contributing & support

Project summary
---------------
Polaris focuses on lightweight telemetry and clear, actionable visualizations for caregivers and learners. The system balances useful analytics (session timelines, focus scores, course progress) with privacy safeguards (no raw content logging, aggregated metrics only).

Product features (high level)
----------------------------
- Activity tracking: active/idle detection, focused session identification
- Dashboard: session timelines, daily/weekly summaries, per-user reports
- Course progress: chapter-level completion tracking and progress aggregation
- Parental controls: domain-level policy rules and lightweight blocking
- Real-time sync: WebSocket-based updates for rules and notifications

Architecture & components
-------------------------
High-level components:

- Browser extension (Manifest v3): collects lightweight events and sends them to backend or buffers when offline.
- Backend API (FastAPI): ingests events, computes metrics, persists to MySQL, exposes secure REST/WebSocket endpoints.
- Frontend dashboard (Vite + React): visualizes activity, manages users/roles, and administers parental rules.
- Optional FAISS index: semantic indexing for RAG features and contextual recommendations.

ASCII architecture diagram

```
                  +-----------------+                +----------------+
                  |   Browser       |  -- HTTPS -->   |  FastAPI       |
                  |   Extension     |                |  Backend + DB  |
                  +--------+--------+                +----+------+----+
                               |                              |      |
                               | WebSocket/HTTPS              |      | (optional)
                               v                              v      v
                        +----+-----+                  +-----+----+   +--------+
                        | Frontend | <--- HTTPS --->  |  MySQL   |   |  FAISS |
                        | Dashboard|                  +----------+   +--------+
                        +----------+
```

Data flow
---------
1. The extension records lightweight events (timestamp, activity state, domain, session markers).
2. Events are sent to the backend over HTTPS or buffered and retried when offline.
3. Backend validates, aggregates, and stores events in MySQL; computes derived metrics (focus score, session durations).
4. Dashboard queries the backend for aggregated views; WebSockets send real-time updates for rules/notifications.

Security & privacy
------------------
- Privacy-first by design: no raw content capture (no page content, search queries, or chat transcripts).
- Data minimization: only store aggregate or domain-level metadata; session identifiers are rotated regularly.
- Transport security: HTTPS required for all API endpoints; WebSocket connections use wss://.
- Access control: Dashboard API uses token-based auth with role checks (parent, learner, admin).

Tech stack
----------
- Frontend: Vite, React, modern JavaScript
- Backend: Python, FastAPI, Uvicorn
- Database: MySQL (relational schema; see `backend/parent_child_connections.sql`)
- Optional: FAISS for embeddings and semantic features
- Dev tooling: Docker, Docker Compose (for local multi-service runs)

Deployment & hosting
--------------------
- Frontend: static hosting (Netlify, Vercel, S3 + CloudFront)
- Backend: containerized (Docker) or serverless (Cloud Run, App Service); requires a managed MySQL instance
- Live demo: https://polaristracker.netlify.app

Local development (quick start)
-----------------------------
1) Backend (Windows example)

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
uvicorn app.main:app --reload --port 8000
```

2) Frontend

```bash
cd frontend
npm install
npm run dev
```

3) Extension (optional)

1. Open `chrome://extensions`
2. Enable Developer Mode
3. Click "Load unpacked" and select the `extension/` folder

Project structure (top-level)
----------------------------

- `backend/` — FastAPI app, migrations, DB init scripts, and requirements
- `frontend/` — Vite + React app and public assets
- `extension/` — Chrome extension source (Manifest v3)


Contributing & review notes for HR
----------------------------------
- Code is organized by component (backend, frontend, extension) for straightforward review.
- Relevant files to inspect for architecture and security: `backend/app/main.py`, `backend/config/settings.py`, `extension/content/`, and `frontend/src/components/`.
- If you want me to produce a short one-page executive summary (PDF or printable Markdown) tailored for HR, I can generate that next.

License
-------
MIT

Contact
-------
Open an issue in this repository or reach out to the maintainer listed in `PROJECT_EXPLAINER.md`.



