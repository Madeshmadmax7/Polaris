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

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

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
