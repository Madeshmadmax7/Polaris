<div align="center">

<br/>

<a href="https://github.com/Madeshmadmax7/Polaris">
  <img src="https://readme-typing-svg.demolab.com?font=Orbitron&size=58&duration=3000&pause=1500&color=FFFFFF&background=09090B00&center=true&vCenter=true&width=850&height=100&lines=POLARIS+TRACKER" alt="POLARIS TRACKER" />
</a>

<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&size=14&duration=4000&pause=1000&color=8B949E&center=true&vCenter=true&width=700&height=30&lines=AI+Powered+Productivity+Analytics+Platform;FastAPI+%7C+React+%7C+Chrome+Extension+%7C+NLP+%7C+FAISS" alt="tagline" />

<br/>
<br/>

![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-Frontend-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Chrome Extension](https://img.shields.io/badge/Chrome-Extension-4285F4?style=for-the-badge&logo=googlechrome&logoColor=white)
![NLP](https://img.shields.io/badge/NLP-AI%20Engine-6A1B9A?style=for-the-badge)
![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-FF6F00?style=for-the-badge)

<br/>
<br/>

<img src="./screenshots/dashboard.png" width="95%" />

<br/>

**Polaris Tracker is an AI-powered productivity intelligence platform designed to monitor user activity, analyze behavioral patterns, and generate intelligent productivity insights through browser telemetry, NLP, and real-time analytics.**

<br/>

<p align="center">

<a href="#features">
  <img src="https://img.shields.io/badge/Features-0D1117?style=for-the-badge&logo=readthedocs&logoColor=white"/>
</a>

<a href="#system-architecture">
  <img src="https://img.shields.io/badge/Architecture-0D1117?style=for-the-badge&logo=dependabot&logoColor=white"/>
</a>

<a href="#technology-stack">
  <img src="https://img.shields.io/badge/Tech%20Stack-0D1117?style=for-the-badge&logo=stackshare&logoColor=white"/>
</a>

<a href="#repository-setup">
  <img src="https://img.shields.io/badge/Setup-0D1117?style=for-the-badge&logo=rocket&logoColor=white"/>
</a>

</p>

</div>

---

## Overview

Polaris Tracker combines a Chrome Extension, FastAPI backend, NLP intelligence engine, and React analytics dashboard into a unified ecosystem capable of tracking activity, analyzing focus sessions, generating semantic productivity insights, and visualizing user behavior in real time.

<br/>

<table width="95%">
<tr>

<td width="50%" valign="top">

## Why Polaris?

- Real-time browser activity monitoring
- AI-powered productivity analysis
- Interactive analytics dashboard
- NLP-driven behavioral intelligence
- Real-time synchronization pipeline
- Lightweight telemetry architecture
- Secure and privacy-focused design
- Intelligent productivity reporting

</td>

<td width="50%" valign="top">

## Built With

- **Frontend:** React · Vite · Tailwind CSS
- **Backend:** FastAPI · Python · WebSockets
- **AI Layer:** NLP · FAISS · Semantic Analysis
- **Database:** MySQL · Redis
- **Extension:** Chrome Manifest V3
- **Infrastructure:** Docker · Linux · GitHub

</td>

</tr>
</table>
---

# Features

## Productivity Analytics Dashboard

<table width="100%">
<tr>
<th width="50%" align="center">Dashboard Overview</th>
<th width="50%" align="center">Productivity Monitoring</th>
</tr>

<tr>
<td align="center" valign="top">

<img src="./screenshots/dashboard.png" alt="Dashboard Overview"/>

</td>

<td align="center" valign="top">

<img src="./screenshots/productivity-dashboard.png" alt="Productivity Monitoring"/>

</td>
</tr>
</table>

<br/>

The analytics dashboard provides comprehensive visualization of user productivity patterns, focus sessions, active time tracking, and behavioral insights.

### Core Capabilities

- Real-time productivity metrics
- Daily and weekly analytics reports
- Interactive visualization panels
- Focus session analysis
- Website usage statistics
- Timeline-based activity tracking
- Session history monitoring
- Progress and consistency analysis

---

## Chrome Extension Tracking

<div align="center">

<img src="./screenshots/img2.png" width="90%" />

</div>

<br/>

The Chrome Extension acts as the telemetry collection layer of Polaris Tracker. It continuously captures browser activity data and synchronizes it with backend infrastructure in real time.

```text
Browser Activity
      ↓
Manifest V3 Extension
      ↓
Activity Processing
      ↓
Secure Backend APIs
      ↓
Analytics Dashboard
```

### Extension Features

- Browser activity collection
- Lightweight telemetry system
- Background synchronization
- Real-time activity streaming
- Manifest V3 architecture
- Low-overhead monitoring
- Secure API communication

---

## NLP Intelligence Engine

<table>
<tr>
<td width="50%">

### AI Capabilities

- Semantic behavior analysis
- NLP-driven activity interpretation
- Productivity recommendation engine
- Behavioral pattern recognition
- AI-generated insights
- FAISS vector similarity search

</td>

<td width="50%">

```text
User Activity
      ↓
Behavioral Processing
      ↓
NLP Semantic Analysis
      ↓
Pattern Recognition
      ↓
AI Productivity Insights
```

</td>
</tr>
</table>

---

## Course Progress & Monitoring

<div align="center">

<img src="./screenshots/ppt-review1-09.png" width="90%" />

</div>

<br/>

Polaris includes intelligent progress tracking systems capable of visualizing completion metrics, consistency analysis, structured monitoring, and productivity progression.

### Monitoring Features

- Progress visualization
- Completion analytics
- Structured tracking system
- Performance monitoring
- Consistency analysis
- Activity-based reporting

---

# System Workflow

<div align="center">

<img src="./screenshots/img1.jpg" width="95%" />

</div>

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
|:---|:---|:---|:---|
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
├── backend/          # FastAPI backend services
├── frontend/         # React analytics dashboard
├── extension/        # Chrome extension telemetry layer
├── screenshots/      # README assets
│
└── README.md
```

---

# Modules

| Module | Description |
|:---|:---|
| Chrome Extension | User activity tracking and telemetry |
| FastAPI Backend | APIs and analytics processing |
| NLP Engine | AI-powered productivity intelligence |
| React Dashboard | Analytics visualization system |
| MySQL Database | Persistent storage layer |
| WebSocket Layer | Real-time synchronization |

---

# Deployment

| Service | Platform |
|:---|:---|
| Frontend | Netlify |
| Backend | Render / VPS |
| Database | MySQL |
| APIs | FastAPI |
| Extension | Chrome Browser |

---

# Repository Setup

<details>
<summary><b>Frontend Setup</b></summary>

```bash
cd frontend
npm install
npm run dev
```

</details>

---

<details>
<summary><b>Backend Setup</b></summary>

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate

pip install -r requirements.txt

uvicorn main:app --reload
```

</details>

---

<details>
<summary><b>Chrome Extension Setup</b></summary>

```bash
# Open chrome://extensions/

# Enable Developer Mode

# Click "Load unpacked"

# Select extension/ folder
```

</details>

---

# Clone Repository

```bash
git clone https://github.com/Madeshmadmax7/Polaris.git
```

---

<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Orbitron&size=34&duration=4000&pause=2000&color=FFFFFF&background=09090B00&center=true&vCenter=true&width=650&height=60&lines=Built+for+Productivity+Analytics" />

<br/>

![Stars](https://img.shields.io/github/stars/Madeshmadmax7/Polaris?style=flat-square&color=white&labelColor=09090b)
![License](https://img.shields.io/badge/License-MIT-white?style=flat-square&labelColor=09090b)
![AI Powered](https://img.shields.io/badge/AI-Powered-white?style=flat-square&labelColor=09090b)

<br/>

Star this repository if you found Polaris useful

</div>
