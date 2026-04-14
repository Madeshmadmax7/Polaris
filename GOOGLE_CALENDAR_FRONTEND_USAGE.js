// ─────────────────────────────────────────────────────────────
// 1. BASIC USAGE - GET AUTH URL
// ─────────────────────────────────────────────────────────────

async function getGoogleAuthUrl() {
  try {
    // No login token needed - endpoint is PUBLIC!
    const response = await fetch(
      "http://127.0.0.1:8000/api/integrations/google-calendar/auth-url"
    );

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    
    if (data.error) {
      console.error("❌ Error:", data.message);
      return null;
    }

    console.log("✅ Got auth URL:", data.auth_url);
    return data.auth_url;

  } catch (error) {
    console.error("❌ Failed to get auth URL:", error.message);
    return null;
  }
}

// ─────────────────────────────────────────────────────────────
// 2. REDIRECT URL - CLICK BUTTON
// ─────────────────────────────────────────────────────────────

function GoogleCalendarLoginButton() {
  const handleClick = async () => {
    const authUrl = await getGoogleAuthUrl();
    if (authUrl) {
      // Redirect user to Google OAuth
      window.location.href = authUrl;
    }
  };

  return (
    <button onClick={handleClick} style={buttonStyle}>
      🔵 Connect Google Calendar
    </button>
  );
}

// ─────────────────────────────────────────────────────────────
// 3. WITH LOADING STATE - BETTER UX
// ─────────────────────────────────────────────────────────────

import { useState } from "react";

function GoogleCalendarConnect() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleConnect = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/integrations/google-calendar/auth-url"
      );

      const data = await response.json();

      if (data.error) {
        setError(data.message);
        return;
      }

      // Redirect to Google
      window.location.href = data.auth_url;

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {error && <p style={{ color: "red" }}>Error: {error}</p>}
      <button onClick={handleConnect} disabled={loading}>
        {loading ? "Connecting..." : "Connect Google Calendar"}
      </button>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// 4. IN SETTINGS COMPONENT
// ─────────────────────────────────────────────────────────────

function IntegrationSettings() {
  const [calendarConnected, setCalendarConnected] = useState(false);
  const [loading, setLoading] = useState(false);

  const connectCalendar = async () => {
    setLoading(true);
    
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/integrations/google-calendar/auth-url"
      );
      
      const { auth_url, error } = await response.json();

      if (error) {
        console.error("Configuration error:", error);
        return;
      }

      // Open in same window (for single-page flow)
      window.location.href = auth_url;

    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="settings-integrations">
      <h2>Integrations</h2>
      
      <div className="integration-item">
        <h3>📅 Google Calendar</h3>
        <p>Status: {calendarConnected ? "✅ Connected" : "❌ Not connected"}</p>
        <button 
          onClick={connectCalendar}
          disabled={loading}
        >
          {loading ? "Connecting..." : "Connect Calendar"}
        </button>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// 5. WITH CUSTOM REDIRECT AFTER AUTH
// ─────────────────────────────────────────────────────────────

async function startGoogleCalendarOAuth(redirectPath = "/settings/integrations") {
  try {
    // Get the auth URL
    const response = await fetch(
      "http://127.0.0.1:8000/api/integrations/google-calendar/auth-url"
    );

    const { auth_url, error } = await response.json();

    if (error) {
      console.error("Failed to get auth URL:", error);
      return;
    }

    // Store where to redirect after OAuth callback
    sessionStorage.setItem("oauth_redirect", redirectPath);

    // Open in new window (optional - instead of redirecting current page)
    // window.open(auth_url, "_blank", "width=600,height=600");
    
    // OR redirect current page
    window.location.href = auth_url;

  } catch (error) {
    console.error("Error starting OAuth:", error);
  }
}

// ─────────────────────────────────────────────────────────────
// 6. HANDLE CALLBACK AFTER USER AUTHORIZES
// ─────────────────────────────────────────────────────────────

// This would be in your /callback or /settings page
import { useEffect } from "react";
import { useSearchParams } from "react-router-dom";

function GoogleCalendarCallback() {
  const [searchParams] = useSearchParams();
  const code = searchParams.get("code");
  const error = searchParams.get("error");

  useEffect(() => {
    if (error) {
      console.error("OAuth error:", error);
      alert("Failed to connect calendar");
      return;
    }

    if (code) {
      // Backend handles the callback at:
      // GET /api/integrations/google-calendar/callback?code=...&state=...
      console.log("✅ Authorization successful!");
      // You can make additional API calls here
    }
  }, [code, error]);

  return <div>✅ Calendar connected! Redirecting...</div>;
}

// ─────────────────────────────────────────────────────────────
// 7. API WRAPPER for Reusability
// ─────────────────────────────────────────────────────────────

const googleCalendarAPI = {
  // Get OAuth URL (PUBLIC - no auth token needed)
  async getAuthUrl() {
    const response = await fetch(
      "http://127.0.0.1:8000/api/integrations/google-calendar/auth-url"
    );
    return response.json();
  },

  // Get connection status
  async getStatus(token) {
    const response = await fetch(
      "http://127.0.0.1:8000/api/integrations/google-calendar/status",
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );
    return response.json();
  },

  // Get upcoming events
  async getEvents(token, maxResults = 10) {
    const response = await fetch(
      `http://127.0.0.1:8000/api/integrations/google-calendar/events?max_results=${maxResults}`,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );
    return response.json();
  },

  // Disconnect calendar
  async disconnect(token) {
    const response = await fetch(
      "http://127.0.0.1:8000/api/integrations/google-calendar/disconnect",
      {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` }
      }
    );
    return response.json();
  }
};

// Usage:
// const { auth_url } = await googleCalendarAPI.getAuthUrl();
// window.location.href = auth_url;

// ─────────────────────────────────────────────────────────────
// 8. FULL COMPONENT EXAMPLE
// ─────────────────────────────────────────────────────────────

import React, { useState } from "react";

export function GoogleCalendarIntegration() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleConnect = async () => {
    setLoading(true);
    setError(null);

    try {
      // No authentication required - public endpoint!
      const response = await fetch(
        "http://127.0.0.1:8000/api/integrations/google-calendar/auth-url"
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const { auth_url, error: responseError } = await response.json();

      if (responseError) {
        setError(responseError);
        return;
      }

      // Redirect user to Google OAuth
      window.location.href = auth_url;

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={containerStyle}>
      <h3>📅 Google Calendar</h3>
      <p style={descriptionStyle}>
        Connect your Google Calendar to sync events
      </p>

      {error && (
        <div style={errorStyle}>
          <strong>Error:</strong> {error}
        </div>
      )}

      <button
        onClick={handleConnect}
        disabled={loading}
        style={buttonStyle(loading)}
      >
        {loading ? "Connecting..." : "Connect Google Calendar"}
      </button>
    </div>
  );
}

// Styles
const containerStyle = {
  padding: "20px",
  border: "1px solid #ddd",
  borderRadius: "8px",
  marginBottom: "20px"
};

const descriptionStyle = {
  color: "#666",
  fontSize: "14px",
  marginBottom: "15px"
};

const errorStyle = {
  padding: "10px",
  backgroundColor: "#fee",
  color: "#c33",
  borderRadius: "4px",
  marginBottom: "10px"
};

const buttonStyle = (disabled) => ({
  padding: "10px 20px",
  backgroundColor: disabled ? "#ccc" : "#4285f4",
  color: "white",
  border: "none",
  borderRadius: "4px",
  cursor: disabled ? "not-allowed" : "pointer",
  fontSize: "16px"
});

export default GoogleCalendarIntegration;

// ─────────────────────────────────────────────────────────────
// NOTES:
// ─────────────────────────────────────────────────────────────

/*
✅ KEY POINTS:

1. NO AUTHENTICATION REQUIRED
   - The /auth-url endpoint is PUBLIC
   - No JWT token needed
   - No Authorization header required

2. CORS CONFIGURED
   - Works from http://127.0.0.1:5173
   - Works from http://localhost:5173
   - In production, update CORS origins in FastAPI

3. OAUTH FLOW
   - Get auth URL from /auth-url
   - Redirect user to URL
   - User authorizes
   - Google redirects back to /callback
   - Backend exchanges code for tokens

4. ENVIRONMENT SETUP
   Make sure .env has:
   - GOOGLE_CLIENT_ID=your-client-id
   - GOOGLE_CLIENT_SECRET=your-secret
   - GOOGLE_REDIRECT_URI=http://localhost:8000/api/integrations/google-calendar/callback

5. ERROR HANDLING
   Endpoint returns proper errors if:
   - GOOGLE_CLIENT_ID missing
   - GOOGLE_REDIRECT_URI missing
   - OAuth service fails

*/
