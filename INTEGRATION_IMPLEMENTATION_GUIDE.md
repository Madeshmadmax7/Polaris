# LifeOS Integrations Implementation Guide

## Overview

This guide covers three major feature implementations:
1. **Google Calendar Integration** - Bi-directional sync of study sessions & deadlines
2. **Mobile Companion PWA** - Progressive Web App for offline-first mobile access
3. **Notion Integration** - One-way sync of study plans, summaries & analytics

---

## 1. GOOGLE CALENDAR INTEGRATION

### Overview
Syncs study sessions and quiz deadlines to Google Calendar. Supports two-way sync.

### Backend Setup

#### 1.1 Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### 1.2 Get Google OAuth Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Enable **Google Calendar API**
4. Create **OAuth 2.0 Desktop** credentials
5. Download as JSON → save as `backend/credentials.json`

#### 1.3 Set Environment Variables
```bash
# .env file
ENCRYPTION_KEY=your-fernet-key-here  # Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

#### 1.4 Database Setup
The models are already created. Run migrations:
```bash
cd backend
alembic upgrade head  # If using Alembic
# OR
python init_db.py    # If using manual setup
```

### API Endpoints

#### Auth & Setup
```bash
# Get OAuth authorization URL
GET /api/integrations/google-calendar/auth-url
Response: { "auth_url": "https://accounts.google.com/..." }

# Handle OAuth callback (called after user authorizes)
POST /api/integrations/google-calendar/callback?code=<auth_code>
Response: { "status": "success", "email": "user@gmail.com" }

# Check integration status
GET /api/integrations/google-calendar/status
Response: {
  "connected": true,
  "email": "user@gmail.com",
  "is_enabled": true,
  "sync_study_sessions": true,
  "sync_deadlines": true,
  "last_sync_at": "2024-03-15T10:30:00"
}

# Disconnect
DELETE /api/integrations/google-calendar/disconnect
```

#### Sync Operations
```bash
# Sync study session (e.g., 2-hour study block)
POST /api/integrations/google-calendar/sync-study-session
Body: {
  "title": "Advanced DSA Study Session",
  "start_time": "2024-03-20T14:00:00Z",
  "end_time": "2024-03-20T16:00:00Z",
  "description": "Dynamic Programming Topic",
  "study_plan_id": "plan-uuid"
}
Response: { "status": "success", "event_id": "google-event-id" }

# Sync deadline (all-day event)
POST /api/integrations/google-calendar/sync-deadline
Body: {
  "title": "Complete Chapter 5: Trees",
  "deadline": "2024-03-25T23:59:59Z",
  "description": "Quiz available after chapter",
  "study_plan_id": "plan-uuid",
  "chapter_id": "chapter-uuid"
}
Response: { "status": "success", "event_id": "google-event-id" }
```

### Frontend Integration

#### 1. Initialize PWA
In `App.jsx`:
```jsx
import { initPWA } from '@/utils/pwa';

useEffect(() => {
  initPWA();
}, []);
```

#### 2. Add Integration Settings Page
```jsx
import IntegrationSettings from '@/pages/IntegrationSettings';

// In your router
<Route path="/settings/integrations" element={<IntegrationSettings />} />
```

#### 3. Auto-Sync on Study Plan Creation
When a study plan is created, automatically sync to calendar:
```jsx
// After creating study plan
const startDate = new Date();
const endDate = new Date();
endDate.setDate(endDate.getDate() + planDuration);

await api.post(`/integrations/google-calendar/sync-study-session`, {
  title: `Study: ${planTitle}`,
  start_time: startDate,
  end_time: endDate,
  description: `Study plan: ${goal}`,
  study_plan_id: planId
});
```

---

## 2. NOTION INTEGRATION

### Overview
One-way sync of study plans, chapter summaries, and analytics to a Notion database.

### Backend Setup

#### 2.1 Install Dependencies
```bash
pip install notion-client==2.2.1
```

#### 2.2 Create Notion Integration
1. Go to [Notion My Integrations](https://www.notion.so/my-integrations)
2. Create new integration
3. Get the **Internal Integration Token** (API key)
4. Create a database for syncing (template: Table with properties)

#### 2.3 Database Properties
Your Notion database should have these columns:
- **Title** (title) - Study plan or summary title
- **Type** (select) - "Study Plan", "Chapter Summary", "Analytics"
- **Status** (status) - Not Started, In Progress, Completed
- **Goal** (rich_text) - Original goal
- **Plan** (rich_text) - Parent study plan (for summaries)
- **Chapters** (number) - Number of chapters
- **Average Score** (number) - Quiz average (for analytics)
- **Attempts** (number) - Total quiz attempts
- **Best Score** (number) - Highest quiz score

### API Endpoints

#### Setup
```bash
# Connect Notion integration
POST /api/integrations/notion/setup
Body: {
  "api_key": "secret_xxxx...",
  "workspace_id": "workspace-id",
  "database_id": "database-id-here"
}
Response: { "status": "success", "message": "Notion integration created" }

# Check connection status
GET /api/integrations/notion/status
Response: {
  "connected": true,
  "is_enabled": true,
  "sync_summaries": true,
  "sync_analytics": true,
  "last_sync_at": "2024-03-15T10:30:00"
}

# Disconnect
DELETE /api/integrations/notion/disconnect
```

#### Sync Operations
```bash
# Sync study plan to Notion
POST /api/integrations/notion/sync-study-plan/{study_plan_id}
Query: ?include_chapters=true
Response: {
  "status": "success",
  "message": "Study plan synced to Notion",
  "page_id": "notion-page-id"
}

# Sync chapter summary
POST /api/integrations/notion/sync-chapter-summary/{chapter_id}
Response: {
  "status": "success",
  "message": "Chapter summary synced to Notion",
  "page_id": "notion-page-id"
}

# Sync analytics
POST /api/integrations/notion/sync-analytics/{study_plan_id}
Response: {
  "status": "success",
  "message": "Analytics synced to Notion",
  "page_id": "notion-page-id"
}
```

### Frontend Integration

In `IntegrationSettings.jsx`, users can:
1. Paste Notion API key
2. Enter database ID
3. Click "Connect Notion"
4. Summaries/analytics auto-sync when chapters complete

---

## 3. MOBILE PWA (PROGRESSIVE WEB APP)

### Overview
Cross-platform mobile app built with React. Works on iOS & Android without native compilation.

### Key Features

#### Offline Support
- Service Worker caches assets (JS, CSS, images)
- API calls fallback to cached responses
- Background sync queues failed requests for retry

#### Installation
- **iOS**: Share → "Add to Home Screen"
- **Android**: Menu → "Install app" or "Add to Home Screen"
- Installable from browser menu

#### Notifications
- Push notifications for quiz reminders
- Deadline alerts
- Achievement unlocked notifications

### Frontend Files

#### 1. Web App Manifest (`manifest.json`)
- Defines app name, icons, theme colors
- Shortcuts to key pages
- Screenshot for app store

#### 2. Service Worker (`public/sw.js`)
- Pre-caches essential assets
- Network-first for APIs (auto-fallback to cache)
- Background sync for offline actions
- Push notification handling

#### 3. PWA Utilities (`src/utils/pwa.js`)
- Service Worker registration
- Offline queue management
- Notification permissions
- Installation prompt

### Usage in React

```jsx
import { initPWA, isPWA, isOnline } from '@/utils/pwa';

useEffect(() => {
  // Initialize PWA features
  const pwaInfo = await initPWA();
  
  console.log("Running as app:", pwaInfo.isPWAMode);
  console.log("Is online:", pwaInfo.isOnline);
}, []);

// Check online status
if (!isOnline()) {
  return <OfflineMessage />;
}

// Queue data for offline sync
import { queueForOfflineSync } from '@/utils/pwa';

const handleQuizSubmit = (answers) => {
  if (!isOnline()) {
    queueForOfflineSync('quiz_attempt', {
      answers,
      timestamp: Date.now()
    });
    alert("Quiz queued. Will submit when online.");
    return;
  }
  
  // Submit normally
};
```

### Deployment/Setup

#### 1. Generate App Icons
Create these images (use any icon creator):
```
/frontend/public/images/
  ├── icon-192.png (192×192)
  ├── icon-512.png (512×512)
  ├── icon-192-maskable.png (with safe zone)
  ├── icon-512-maskable.png
  ├── badge-72.png (72×72)
  └── screenshot-*.png
```

#### 2. Build Frontend
```bash
cd frontend
npm run build
```

#### 3. Serve with HTTPS (Required)
PWA requires HTTPS:
```bash
# Development with localhost (localhost works)
npm run dev

# Production: Deploy to Vercel, Netlify, or with HTTPS
```

#### 4. Test PWA
1. Open in Chrome DevTools → Application tab
2. Check "Manifest", "Service Worker", "Cache Storage"
3. Install via browser menu
4. Go offline (DevTools → Network → offline)
5. Visit cached pages - should work

### Lighthouse Audit

```bash
# Check PWA readiness
lighthouse https://your-domain.com --view
```

Should score 90+ in PWA metrics.

---

## Database Schema Changes

### New Tables Added

```sql
-- Google Calendar Integration
CREATE TABLE google_calendar_integrations (
  id VARCHAR(36) PRIMARY KEY,
  user_id VARCHAR(36) UNIQUE NOT NULL,
  email VARCHAR(255) NOT NULL,
  access_token TEXT NOT NULL,
  refresh_token TEXT NOT NULL,
  calendar_id VARCHAR(255) DEFAULT 'primary',
  is_enabled BOOLEAN DEFAULT TRUE,
  sync_study_sessions BOOLEAN DEFAULT TRUE,
  sync_deadlines BOOLEAN DEFAULT TRUE,
  last_sync_at DATETIME NULL,
  created_at DATETIME DEFAULT UTC_TIMESTAMP,
  updated_at DATETIME DEFAULT UTC_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE calendar_events (
  id VARCHAR(36) PRIMARY KEY,
  user_id VARCHAR(36) NOT NULL,
  google_event_id VARCHAR(255) NOT NULL,
  event_type VARCHAR(50) NOT NULL,
  study_plan_id VARCHAR(36) NULL,
  chapter_id VARCHAR(255) NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT NULL,
  start_time DATETIME NOT NULL,
  end_time DATETIME NOT NULL,
  deleted BOOLEAN DEFAULT FALSE,
  synced_at DATETIME DEFAULT UTC_TIMESTAMP,
  last_modified DATETIME DEFAULT UTC_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  UNIQUE KEY (user_id, google_event_id)
);

-- Notion Integration
CREATE TABLE notion_integrations (
  id VARCHAR(36) PRIMARY KEY,
  user_id VARCHAR(36) UNIQUE NOT NULL,
  notion_api_key TEXT NOT NULL,
  notion_workspace_id VARCHAR(255) NOT NULL,
  database_id VARCHAR(255) NOT NULL,
  is_enabled BOOLEAN DEFAULT TRUE,
  sync_summaries BOOLEAN DEFAULT TRUE,
  sync_analytics BOOLEAN DEFAULT TRUE,
  last_sync_at DATETIME NULL,
  created_at DATETIME DEFAULT UTC_TIMESTAMP,
  updated_at DATETIME DEFAULT UTC_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE notion_pages (
  id VARCHAR(36) PRIMARY KEY,
  user_id VARCHAR(36) NOT NULL,
  notion_page_id VARCHAR(255) UNIQUE NOT NULL,
  page_type VARCHAR(50) NOT NULL,
  study_plan_id VARCHAR(36) NULL,
  chapter_id VARCHAR(255) NULL,
  title VARCHAR(255) NOT NULL,
  synced_at DATETIME DEFAULT UTC_TIMESTAMP,
  last_modified DATETIME DEFAULT UTC_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX (user_id, page_type)
);
```

---

## Security Considerations

### API Keys & Tokens

1. **Encryption**: All tokens stored encrypted with Fernet
   ```python
   ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")  # Must be 44-char base64
   ```

2. **Secrets**: Store in `.env` or environment variables
   ```
   ENCRYPTION_KEY=your-key-here
   GOOGLE_CREDENTIALS_PATH=backend/credentials.json
   ```

3. **Scopes**: Request minimal permissions
   - Google Calendar: Only `calendar` scope
   - Notion: Only database access needed

### Rate Limiting
- Google Calendar: 1000 req/day per user
- Notion: 3-4 req/sec per integration

### CORS Setup
Already configured in `settings.py`:
```python
CORS_ORIGINS = [
    "http://localhost:5173",  # Frontend dev
    "http://localhost:3000",
    "https://yourdomain.com"  # Production
]
```

---

## Testing

### Unit Tests

```python
# backend/tests/test_integrations.py
import pytest
from app.services.google_calendar_service import GoogleCalendarService

@pytest.fixture
def cal_service(db_session):
    return GoogleCalendarService(db_session)

def test_google_calendar_oauth_url(cal_service):
    url = cal_service.get_auth_url("user-id", "http://localhost:5173/callback")
    assert "accounts.google.com" in url

def test_notion_setup(cal_service):
    result = service.create_integration(
        user_id="user-id",
        api_key="secret_xxx",
        workspace_id="ws-id",
        database_id="db-id"
    )
    assert result["status"] == "success"
```

### E2E Tests

```javascript
// frontend/tests/integrations.e2e.js
describe("Google Calendar Integration", () => {
  test("Should connect to Google Calendar", async () => {
    await page.goto("http://localhost:5173/settings/integrations");
    
    await page.click("text=Connect Google Calendar");
    // OAuth flow...
    
    await expect(page).toHaveText("Connected as");
  });
});
```

---

## Troubleshooting

### Google Calendar
**Issue**: OAuth fails with "redirect_uri mismatch"
- Fix: Redirect URI in code must exactmatch Google Cloud Console

**Issue**: Tokens expire
- Fix: Service automatically refreshes with refresh_token

### Notion
**Issue**: "404 - Database not found"
- Fix: Verify database_id is correct (find in Notion URL)
- Fix: Ensure integration has access to database

### PWA
**Issue**: Service Worker not registering
- Fix: Must be HTTPS (localhost OK for dev)
- Fix: Clear cache: DevTools → Application → Clear Storage

**Issue**: Offline pages show blank
- Fix: Pre-cache HTML files in sw.js

---

## Next Steps

1. **Email Notifications**: Send notification when study plan created
2. **Slack Integration**: Post daily progress summaries
3. **Zapier**: Connect to 1000+ apps via Zapier
4. **Apple Reminders**: Sync to iOS native reminders
5. **Habit Tracking**: Auto-sync with Habit Tracker apps

---

## Reference

- [Google Calendar API Docs](https://developers.google.com/calendar)
- [Notion API Reference](https://developers.notion.com/)
- [MDN PWA Guide](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
- [Service Workers](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
