<h1 align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Orbitron&weight=800&size=42&duration=3000&pause=1000&color=FFFFFF&center=true&vCenter=true&width=1000&lines=POLARIS+TRACKER;AI+Powered+Productivity+Analytics+Platform;FastAPI+%7C+React+%7C+Chrome+Extension+%7C+NLP" />
</h1>

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/React-Frontend-20232A?style=for-the-badge&logo=react&logoColor=61DAFB"/>
  <img src="https://img.shields.io/badge/Chrome-Extension-4285F4?style=for-the-badge&logo=googlechrome&logoColor=white"/>
  <img src="https://img.shields.io/badge/NLP-AI%20Engine-6A1B9A?style=for-the-badge"/>
</p>

---

# Polaris Tracker

Polaris Tracker is an AI-powered productivity analytics and monitoring platform designed to track user activity, analyze focus sessions, generate productivity insights, and provide intelligent monitoring through a browser extension and analytics dashboard.

The platform integrates real-time activity tracking, NLP-powered analysis, analytics visualization, and scalable backend infrastructure into a unified monitoring ecosystem.

---

## Dashboard

<p align="center">
  <img src="./screenshots/dashboard.png" width="100%" alt="Dashboard"/>
</p>

---

# Core Features

## Productivity Monitoring
- Active and idle session tracking
- Focus time analysis
- Website usage statistics
- Session history analytics
- Real-time activity updates

## Analytics Dashboard
- Interactive productivity metrics
- Daily and weekly reports
- Timeline visualization
- User activity insights
- Progress monitoring

<p align="center">
  <img src="./screenshots/productivity-dashboard.png" width="100%" alt="Productivity-Dashboard"/>
</p>

## Chrome Extension
- Browser activity collection
- Lightweight telemetry system
- Background monitoring
- Real-time synchronization
- Manifest V3 architecture

## NLP Intelligence
- Behavior pattern analysis
- Semantic processing
- Productivity insight generation
- Recommendation engine
- Intelligent analytics

## Security & Privacy
- Token-based authentication
- Secure API communication
- Privacy-first architecture
- HTTPS and WebSocket security
- Minimal telemetry collection

---

# System Architecture

```text
 ┌──────────────────────────┐
 │    Chrome Extension      │
 │ Activity Tracking Layer  │
 └────────────┬─────────────┘
              │
              │ HTTPS / WSS
              ▼
 ┌──────────────────────────┐
 │      FastAPI Backend     │
 │ Authentication + APIs    │
 │ Analytics Processing     │
 └────────────┬─────────────┘
              │
      ┌───────┴────────┐
      ▼                ▼
 ┌───────────┐   ┌─────────────┐
 │   MySQL   │   │ NLP Engine  │
 │ Database  │   │ + FAISS AI  │
 └───────────┘   └─────────────┘
              │
              ▼
 ┌──────────────────────────┐
 │     React Dashboard      │
 │ Productivity Analytics   │
 └──────────────────────────┘
```

---

# Technology Stack

| Frontend | Backend | AI / NLP | Infrastructure |
|---|---|---|---|
| React.js | FastAPI | NLP Processing | MySQL |
| Vite | Python | FAISS Vector Search | Redis |
| JavaScript | Uvicorn | Semantic Analysis | Docker |
| HTML5 | REST APIs | Recommendation Engine | Linux |
| CSS3 | WebSockets | AI Analytics | GitHub |
| Tailwind CSS | Authentication APIs | Data Intelligence | Postman |

---

# Application Flow

```text
User Activity
      │
      ▼
Chrome Extension
      │
      ▼
FastAPI Backend APIs
      │
 ┌────┴─────┐
 ▼          ▼
MySQL     NLP Engine
 │          │
 └────┬─────┘
      ▼
React Dashboard
      │
      ▼
Analytics & Insights
```

---

# Project Structure

```bash
Polaris/
│
├── backend/
├── frontend/
├── extension/
├── screenshots/
|
└── README.md
```

---

# Modules

| Module | Description |
|---|---|
| Chrome Extension | User activity tracking |
| FastAPI Backend | APIs and analytics processing |
| NLP Engine | AI-powered insight generation |
| React Dashboard | Productivity visualization |
| MySQL Database | Persistent data storage |
| WebSocket Layer | Real-time synchronization |

---

# Deployment

| Service | Platform |
|---|---|
| Frontend | Netlify |
| Backend | Render / VPS |
| Database | MySQL |
| APIs | FastAPI |
| Extension | Chrome Browser |

---

# Repository

```bash
git clone https://github.com/Madeshmadmax7/Polaris.git
```
