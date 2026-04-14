# Integration Setup Checklist

## Quick Start - Get Everything Running in 15 Minutes

### Phase 1: Backend Setup (5 min)

- [ ] **Install Dependencies**
  ```bash
  cd backend
  pip install -r requirements.txt
  ```

- [ ] **Set Encryption Key**
  ```bash
  # Generate key
  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  
  # Add to .env
  ENCRYPTION_KEY=<generated-key>
  ```

- [ ] **Create Database Tables**
  ```bash
  # Using init_db.py
  python init_db.py
  
  # OR with Alembic
  alembic upgrade head
  ```

- [ ] **Update main.py**
  ```python
  # Already done - integrations router imported and registered
  from app.routes import ... integrations
  app.include_router(integrations.router)
  ```

### Phase 2: Google Calendar (Optional - 3 min)

- [ ] **Get OAuth Credentials** (if enabling calendar syncing)
  1. Go to [Google Cloud Console](https://console.cloud.google.com/)
  2. Create project → Enable Calendar API
  3. Create OAuth 2.0 credentials (Desktop app)
  4. Download JSON → save as `backend/credentials.json`

- [ ] **Test Endpoint**
  ```bash
  curl http://localhost:8000/api/integrations/google-calendar/status
  ```

### Phase 3: Notion Setup (Optional - 2 min)

- [ ] **Create Notion Database**
  1. Go to [notion.so/my-integrations](https://www.notion.so/my-integrations)
  2. Create new integration → Copy API Key
  3. Create database with properties (see guide)
  4. Share database with integration

- [ ] **Test Endpoint**
  ```bash
  curl http://localhost:8000/api/integrations/notion/status
  ```

### Phase 4: PWA Setup (5 min)

- [ ] **Create Icon Images**
  Place in `frontend/public/images/`:
  ```
  icon-192.png       (192×192 - required)
  icon-512.png       (512×512 - required)
  icon-192-maskable.png
  icon-512-maskable.png
  badge-72.png
  screenshot-1.png
  ```

- [ ] **Verify manifest.json**
  ```bash
  # Already created - check paths are correct
  ls frontend/manifest.json
  ```

- [ ] **Verify Service Worker**
  ```bash
  ls frontend/public/sw.js
  ```

- [ ] **Check index.html**
  - [x] `<link rel="manifest" href="/manifest.json">`
  - [x] `<meta name="theme-color">`
  - [x] `<meta name="apple-mobile-web-app-capable">`

- [ ] **Initialize PWA in App.jsx**
  ```jsx
  import { initPWA } from '@/utils/pwa';

  useEffect(() => {
    initPWA();
  }, []);
  ```

- [ ] **Add Integration Settings Page** (already created)
  ```jsx
  <Route path="/settings/integrations" element={<IntegrationSettings />} />
  ```

---

## Start Servers

### Terminal 1 - Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Terminal 2 - Frontend
```bash
cd frontend
npm install
npm run dev
# Opens http://localhost:5173
```

### Terminal 3 - MySQL (if not running)
```bash
mysql -u root -p
# Or Windows Service
```

---

## Test Each Feature

### Test Google Calendar
1. Go to http://localhost:5173/settings/integrations
2. Click "Connect Google Calendar"
3. Authorize with your Google account
4. Should show "Connected as your@gmail.com"

### Test Notion
1. Go to http://localhost:5173/settings/integrations
2. Paste Notion API key
3. Enter Workspace ID & Database ID
4. Click "Connect Notion"
5. Should show "Notion database connected"

### Test PWA
1. Go to http://localhost:5173
2. Open DevTools → Application tab
3. Check "Service Worker" - should show registered
4. Check "Manifest" - should show valid
5. Open "Add to Home Screen" prompt

### Test Offline
1. DevTools → Network tab → set to "Offline"
2. Refresh page - should still load
3. Try clicking links - cached pages load
4. Go back online → page updates

---

## File Checklist

### Backend Files Created/Modified
- ✅ `backend/requirements.txt` - Added google-auth-oauthlib, notion-client, python-dateutil
- ✅ `backend/app/models/models.py` - Added GoogleCalendarIntegration, NotionIntegration models
- ✅ `backend/app/services/google_calendar_service.py` - New file
- ✅ `backend/app/services/notion_service.py` - New file
- ✅ `backend/app/routes/integrations.py` - New file
- ✅ `backend/app/schemas/schemas.py` - Added integration schemas
- ✅ `backend/app/main.py` - Added integrations router

### Frontend Files Created/Modified
- ✅ `frontend/index.html` - Added PWA metadata & manifest link
- ✅ `frontend/manifest.json` - PWA web app manifest
- ✅ `frontend/public/sw.js` - Service Worker
- ✅ `frontend/src/utils/pwa.js` - PWA utilities
- ✅ `frontend/src/pages/IntegrationSettings.jsx` - Integration UI

### Documentation
- ✅ `INTEGRATION_IMPLEMENTATION_GUIDE.md` - Full implementation guide
- ✅ `INTEGRATION_SETUP_CHECKLIST.md` - This file

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        BROWSER (PWA)                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Service Worker                                       │  │
│  │  - Offline caching                                    │  │
│  │  - Background sync                                    │  │
│  │  - Push notifications                                 │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  React App → IntegrationSettings.jsx                  │  │
│  │  - Google Calendar OAuth                              │  │
│  │  - Notion API setup                                   │  │
│  │  - PWA install prompt                                 │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────┬──────────────────────────────────────────────┘
               │ HTTPS
        ┌──────▼──────────────────────────────────────────┐
        │         FastAPI Backend (Port 8000)              │
        │                                                  │
        │  ┌──────────────────────────────────────────┐  │
        │  │ /api/integrations/google-calendar/*      │  │
        │  │ - Auth, sync, status, disconnect        │  │
        │  └──────────────────────────────────────────┘  │
        │                                                  │
        │  ┌──────────────────────────────────────────┐  │
        │  │ /api/integrations/notion/*               │  │
        │  │ - Setup, sync-plan, sync-summary, etc.   │  │
        │  └──────────────────────────────────────────┘  │
        │                                                  │
        │  ┌──────────────────────────────────────────┐  │
        │  │  Google Calendar API Client              │  │
        │  └──────────────────────────────────────────┘  │
        │                                                  │
        │  ┌──────────────────────────────────────────┐  │
        │  │  Notion API Client                       │  │
        │  └──────────────────────────────────────────┘  │
        └──────┬──────────────────────────────────────────┘
               │
        ┌──────┴─────────────────────────────────────┐
        │                                             │
    ┌───▼──────────────┐                    ┌──────▼─────┐
    │   MySQL Database │                    │ Google     │
    │                  │                    │ Calendar / │
    │ - Calendar creds │                    │ Notion     │
    │ - Notion creds   │                    │ APIs       │
    │ - Sync status    │                    └────────────┘
    └──────────────────┘
```

---

## Environment Variables Template

```bash
# .env file for backend
ENCRYPTION_KEY=<your-fernet-key>
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/lifeos
JWT_SECRET=your-jwt-secret-key

# Google Calendar (optional)
GOOGLE_CREDENTIALS_PATH=backend/credentials.json

# Notion (optional)
# No env vars needed - user provides API key via UI
```

---

## Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| "Manifest not found" | index.html missing link | Add `<link rel="manifest" href="/manifest.json">` |
| Service Worker fails to register | HTTP not HTTPS | Use localhost (both work), not IP address |
| Google OAuth fails | Redirect URI mismatch | Match exactly in Google Cloud Console |
| Notion "404 database not found" | Wrong database ID | Get ID from Notion database URL |
| PWA won't install | Not HTTPS | Deploy to Vercel/Netlify or use localhost |
| Offline pages blank | Assets not cached | Add paths to PRECACHE_ASSETS in sw.js |

---

## Next Phase: Advanced Setup

After completing above, consider:

1. **Analytics Dashboard**
   - Which features are most used?
   - Integration success rates
   - User retention metrics

2. **Automated Sync**
   - Auto-sync deadlines when study plan created
   - Scheduled daily summary syncs to Notion
   - Calendar reminders → Push notifications

3. **Advanced PWA**
   - Biometric unlock (Face ID / fingerprint)
   - Home screen widgets (Android 12+)
   - Share target (share PDFs to LifeOS from browser)

4. **Notifications**
   - Break reminders
   - Quiz ready alerts
   - Friend activity (social features)

---

## Support

For issues:
1. Check logs: `docker logs lifeos-backend`
2. Check Network tab in DevTools
3. See INTEGRATION_IMPLEMENTATION_GUIDE.md for detailed docs
4. Review service logs for specific errors

Generated: March 17, 2026
Version: 1.0
