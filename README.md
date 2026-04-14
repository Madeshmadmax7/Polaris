# LifeOS

**Hybrid AI-Powered Digital Well-Being, Adaptive Learning & Ethical Parental Control Platform**

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Chrome Extension│◄──►│  FastAPI Backend  │◄──►│  React Dashboard│
│  (Manifest v3)  │    │  + WebSockets     │    │  (Vite + React) │
└────────┬────────┘    └────────┬─────────┘    └─────────────────┘
         │                      │
         │              ┌───────┴───────┐
         │              │               │
         │         ┌────▼────┐    ┌─────▼─────┐
         │         │  MySQL  │    │   FAISS   │
         │         │Database │    │Vector Store│
         │         └─────────┘    └───────────┘
         │
    ┌────▼──────────┐
    │ declarativeNet │
    │ Request Rules  │
    └───────────────┘
```

## Quick Start

### 1. Database Setup
1. Ensure **MySQL** is running on port `3306`.
2. Create the database:
   ```bash
   cd backend
   python init_db.py
   ```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 4. Extension Setup
1. Open `chrome://extensions`
2. Enable **Developer Mode**
3. Click **Load unpacked**
### 4. Extension Setup
1. Open `chrome://extensions`
2. Enable **Developer Mode**
3. Click **Load unpacked**
4. Select the `extension/` folder

## Key Features

- **Smart Activity Tracking** – Active/idle detection, focus factor analysis
- **Productivity Scoring** – Server-side mathematical model with fragmentation dampening
- **RAG Learning Planner** – Syllabus-grounded AI study plans via FAISS
- **Adaptive Quizzes** – Context-aware quiz generation with difficulty scaling
- **Ethical Parental Controls** – Domain-level visibility, network-layer blocking
- **Privacy-First** – No full URLs, no search queries, no chat content logged
- **Offline-First** – Smart buffering with retry-on-reconnect
- **Real-time Sync** – WebSocket-based blocking rule propagation

## License
MIT

