# Polaris Tracker

Polaris is a lightweight tracker and parental-awareness dashboard that helps families and learners understand digital activity, focus, and study progress while respecting privacy.

Live demo: https://polaristracker.netlify.app

Overview
--------
Polaris provides a browser extension for lightweight activity tracking, a backend API for processing and persistence, and a web dashboard for visualization and parental controls.

Core features
-------------
- Activity & focus tracking (idle/active detection)
- User-friendly dashboard with session timelines and aggregated metrics
- Study progress tracking and simple course/chapter completion states
- Privacy-preserving design — minimal telemetry and no raw chat or query logging
- Real-time sync and rule propagation via WebSockets

Tech stack
----------
- Frontend: Vite + React
- Backend: FastAPI + Uvicorn
- Database: MySQL (or compatible)
- Optional: FAISS for semantic indexing

Quick start (developer)
-----------------------
Clone the repo and follow these steps to run locally.

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

3) Chrome extension (optional)

1. Open `chrome://extensions` in Chrome/Edge
2. Enable Developer Mode
3. Click "Load unpacked" and select the `extension/` folder

Screenshots
-----------
Replace these placeholder images with your actual screenshots. Suggested path: `docs/screenshots/` or `frontend/public/screenshots/`.

<!-- Centered large screenshots (replace paths with your images) -->
<p align="center">
   <img src="docs/screenshots/homepage.png" alt="Polaris Homepage" width="900" />
</p>

<p align="center">
   <img src="docs/screenshots/dashboard.png" alt="Dashboard" width="900" />
</p>

<p align="center">
   <img src="docs/screenshots/extension.png" alt="Extension UI" width="600" />
</p>

If you want the images to display while working locally, add the files above and commit them; the markdown will render automatically on GitHub.

Deployment
----------
- The live demo is hosted at: https://polaristracker.netlify.app
- Frontend can be deployed to Netlify/Vercel; backend can be deployed to any container or cloud VM and configured with the production database.

Contributing
------------
- Fork the repository and open a pull request with a clear description of changes.
- For UI changes, include screenshots and short testing notes.

License
-------
MIT

Contact
-------
For questions, reach out via the project maintainer contact or open an issue in this repository.


