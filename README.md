<<<<<<< HEAD
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
- Screenshots (placeholders removed — add files in `docs/screenshots/`)

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
=======
# Polaris Tracker

Polaris Tracker is a privacy-first activity monitoring and analytics platform designed for students and families. It provides insights into device usage, focus behavior, and learning progress while ensuring that no sensitive user content is collected or stored.

Live Demo: https://polaristracker.netlify.app

---

## Overview

Polaris Tracker delivers meaningful productivity insights using lightweight data collection and clear visualizations. The system is designed to balance usability and privacy by collecting only essential metadata and avoiding intrusive tracking.

---

## Features

- Activity Tracking  
  Detects active and idle states, and identifies focused work sessions

- Analytics Dashboard  
  Displays session timelines, daily and weekly summaries, and per-user reports

- Course Progress Tracking  
  Tracks chapter-level progress and aggregates learning metrics

- Parental Controls  
  Enables domain-level rules and lightweight blocking

- Real-time Updates  
  Uses WebSockets for live synchronization of rules and notifications

---

## Architecture Diagram

```
                   +----------------------+
                   |   Browser Extension  |
                   |   (Manifest v3)      |
                   |----------------------|
                   | - Activity Tracking  |
                   | - Idle Detection     |
                   | - Event Buffering    |
                   +----------+-----------+
                              |
                              | HTTPS / WebSocket
                              v
                   +----------+-----------+
                   |     Backend API      |
                   |     (FastAPI)        |
                   |----------------------|
                   | - Event Processing   |
                   | - Metric Computation |
                   | - Auth & APIs        |
                   +----+-----------+-----+
                        |           |
                        |           |
                        v           v
              +---------+--+   +----+----------+
              |  MySQL DB  |   |   FAISS Index |
              |-------------|  |---------------|
              | - Events    |  | - Embeddings  |
              | - Sessions  |  | - Search      |
              | - Users     |  | (Optional)    |
              +-------------+  +--------------+

                              ^
                              |
                              | HTTPS / WebSocket
                              |
                   +----------+-----------+
                   |   Frontend Dashboard |
                   |   (React + Vite)     |
                   |----------------------|
                   | - Analytics UI       |
                   | - Reports            |
                   | - Parental Controls  |
                   +----------------------+
```

---

## System Components

### Browser Extension
- Captures activity events such as timestamp, domain, and activity state  
- Detects active and idle sessions  
- Buffers events locally when offline  
- Sends batched data to backend  

### Backend (FastAPI)
- Receives and validates incoming data  
- Aggregates events into sessions  
- Computes metrics such as focus score and usage duration  
- Provides REST APIs and WebSocket endpoints  
- Handles authentication and authorization  

### Database (MySQL)
- Stores event logs and session summaries  
- Maintains user relationships and configurations  
- Optimized for time-based queries  

### Frontend (React + Vite)
- Displays analytics dashboards  
- Shows reports and insights  
- Allows configuration of parental controls  
- Connects using REST APIs and WebSockets  

### FAISS (Optional)
- Enables semantic search and recommendation features  
- Can be used for future AI-based insights  

---

## Data Flow

```
1. Extension captures activity events
2. Events are batched and sent via HTTPS
3. Backend processes and stores data in MySQL
4. Aggregation layer computes metrics
5. Frontend fetches processed data
6. WebSockets push real-time updates
```

---

## Security and Privacy

- No content tracking (no keystrokes, page content, or messages)
- Only domain-level and session metadata is stored
- HTTPS and secure WebSocket (WSS) communication
- Token-based authentication
- Role-based access control

---

## Tech Stack

Frontend:
- React
- Vite
- JavaScript

Backend:
- Python
- FastAPI
- Uvicorn

Database:
- MySQL

Optional:
- FAISS

Tools:
- Docker
- Docker Compose

---

## Deployment

Frontend:
- Netlify / Vercel / Static Hosting

Backend:
- Docker containers or cloud platforms (e.g., Google Cloud Run)

Database:
- Managed MySQL instance

---

## Local Development

### Backend
>>>>>>> 732a97847fdbc619a651455ce2db5a8cde082085

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
uvicorn app.main:app --reload --port 8000
```

<<<<<<< HEAD
2) Frontend
=======
### Frontend
>>>>>>> 732a97847fdbc619a651455ce2db5a8cde082085

```bash
cd frontend
npm install
npm run dev
```

<<<<<<< HEAD
3) Extension (optional)

1. Open `chrome://extensions`
2. Enable Developer Mode
3. Click "Load unpacked" and select the `extension/` folder

Project structure (top-level)
----------------------------

- `backend/` — FastAPI app, migrations, DB init scripts, and requirements
- `frontend/` — Vite + React app and public assets
- `extension/` — Chrome extension source (Manifest v3)
- `docs/` — (recommended) place for screenshots, deployment notes, and diagrams


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



=======
### Extension

1. Open chrome://extensions  
2. Enable Developer Mode  
3. Click "Load unpacked"  
4. Select the extension folder  

---

## Project Structure

```
backend/     FastAPI application and database scripts  
frontend/    React dashboard  
extension/   Browser extension (Manifest v3)  
docs/        Documentation and assets  
```

---

## License

MIT

---

## Contact

Open an issue in the repository for questions or contributions.
>>>>>>> 732a97847fdbc619a651455ce2db5a8cde082085
