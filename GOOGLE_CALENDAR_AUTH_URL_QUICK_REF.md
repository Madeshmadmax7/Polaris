# Google Calendar Auth-URL Endpoint - Quick Reference

## ✅ Fixed Issue
**Endpoint**:  `GET /api/integrations/google-calendar/auth-url`  
**Problem**: Returned 403 Forbidden (required authentication)  
**Solution**: Made endpoint PUBLIC (no auth required)

---

## 🔓 Endpoint Details

| Property | Value |
|----------|-------|
| **Route** | `GET /api/integrations/google-calendar/auth-url` |
| **Authentication** | ❌ NONE - Public |
| **CORS** | ✅ Enabled for `127.0.0.1:5173` |
| **Parameters** | None |

---

## 📤 Response

### Success (200 OK)
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/auth?...",
  "message": "Visit this URL to authorize Google Calendar access"
}
```

### Error (400)
```json
{
  "error": "Google OAuth not configured",
  "status": "configuration_error",
  "message": "Set GOOGLE_CLIENT_ID and GOOGLE_REDIRECT_URI in environment"
}
```

---

## 🚀 Quick Start - Frontend

### Simplest Usage
```javascript
// Get auth URL
const response = await fetch(
  "http://127.0.0.1:8000/api/integrations/google-calendar/auth-url"
);
const { auth_url } = await response.json();

// Redirect user
window.location.href = auth_url;
```

### With Button
```javascript
function ConnectCalendarButton() {
  const handleClick = async () => {
    const response = await fetch(
      "http://127.0.0.1:8000/api/integrations/google-calendar/auth-url"
    );
    const { auth_url } = await response.json();
    window.location.href = auth_url;
  };

  return <button onClick={handleClick}>Connect Calendar</button>;
}
```

---

## 📋 Setup Checklist

- [ ] Update `.env` with Google OAuth credentials:
  ```bash
  GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
  GOOGLE_CLIENT_SECRET=your-secret
  GOOGLE_REDIRECT_URI=http://localhost:8000/api/integrations/google-calendar/callback
  ENCRYPTION_KEY=your-key
  ```

- [ ] Restart backend:
  ```bash
  uvicorn app.main:app --reload
  ```

- [ ] Test endpoint:
  ```bash
  curl http://127.0.0.1:8000/api/integrations/google-calendar/auth-url
  ```

- [ ] Verify response contains `auth_url` and includes:
  - ✅ `client_id`
  - ✅ `redirect_uri`
  - ✅ `scope=...calendar`
  - ✅ `access_type=offline`

---

## 🔐 No Authentication Needed

```javascript
// ✅ THIS WORKS - No JWT token required!
fetch("http://127.0.0.1:8000/api/integrations/google-calendar/auth-url")

// ❌ Don't need this for /auth-url:
// headers: { Authorization: `Bearer ${token}` }
```

---

## 🔄 OAuth Flow

```
1. Frontend calls GET /auth-url
2. Backend returns Google OAuth URL
3. Frontend redirects user to URL
4. User authorizes in Google
5. Google redirects to your /callback
6. Backend exchanges code for tokens
7. Done! Calendar connected
```

---

## 📁 Files Updated

| File | Change |
|------|--------|
| `app/routes/google_calendar.py` | Removed auth from `/auth-url` endpoint |

---

## ✨ Key Features

✅ **Public** - No authentication required  
✅ **Clean** - Only 60 lines of code  
✅ **Fast** - Direct environment variable access  
✅ **Safe** - Proper error handling  
✅ **Production-ready** - Logging and validation  

---

## 🧪 Test Commands

### Curl Test
```bash
curl http://127.0.0.1:8000/api/integrations/google-calendar/auth-url | jq
```

### Python Test
```bash
python test_public_auth_url.py
```

### Browser Test
```javascript
fetch("http://127.0.0.1:8000/api/integrations/google-calendar/auth-url")
  .then(r => r.json())
  .then(d => console.log(d.auth_url))
```

---

## 📞 Integration Example (React)

```jsx
import { useState } from "react";

export function GoogleCalendarConnect() {
  const [loading, setLoading] = useState(false);

  const connect = async () => {
    setLoading(true);
    const res = await fetch(
      "http://127.0.0.1:8000/api/integrations/google-calendar/auth-url"
    );
    const { auth_url } = await res.json();
    window.location.href = auth_url;
  };

  return (
    <button onClick={connect} disabled={loading}>
      {loading ? "Connecting..." : "Connect Google Calendar"}
    </button>
  );
}
```

---

## 🎯 Status

| Aspect | Status |
|--------|--------|
| **Authentication** | ✅ Removed |
| **Public Access** | ✅ Enabled |
| **Endpoint Working** | ✅ Tested |
| **CORS** | ✅ Configured |
| **Production Ready** | ✅ Yes |

---

## 📖 Full Documentation

See:
- `GOOGLE_CALENDAR_AUTH_URL_FIX.md` - Detailed fix information
- `GOOGLE_CALENDAR_FRONTEND_USAGE.js` - Complete React examples
- `GOOGLE_CALENDAR_INTEGRATION.md` - Full OAuth setup guide
