# LifeOS Integration API Reference

## Base URL
```
http://localhost:8000/api
```

---

## Google Calendar Integration

### 1. Get OAuth Authorization URL
Generate URL for user to authorize LifeOS to access their Google Calendar.

**Request:**
```http
GET /integrations/google-calendar/auth-url
Authorization: Bearer <jwt-token>
```

**Response:**
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?...",
  "message": "Visit this URL to authorize Google Calendar access"
}
```

**Usage:**
```javascript
// Frontend
const response = await fetch('/api/integrations/google-calendar/auth-url');
const { auth_url } = await response.json();
window.location.href = auth_url;  // Redirect user
```

---

### 2. OAuth Callback Handler
Process the authorization code returned from Google.

**Request:**
```http
POST /integrations/google-calendar/callback?code=<auth-code>
Authorization: Bearer <jwt-token>
```

**Response:**
```json
{
  "status": "success",
  "message": "Google Calendar connected successfully",
  "email": "user@gmail.com"
}
```

**Notes:**
- Called automatically after user authorizes
- Tokens are encrypted and stored in database
- No further action needed from user

---

### 3. Check Integration Status
Get current Google Calendar connection status.

**Request:**
```http
GET /integrations/google-calendar/status
Authorization: Bearer <jwt-token>
```

**Response (Connected):**
```json
{
  "connected": true,
  "email": "user@gmail.com",
  "is_enabled": true,
  "sync_study_sessions": true,
  "sync_deadlines": true,
  "last_sync_at": "2024-03-15T10:30:00Z",
  "calendar_id": "primary"
}
```

**Response (Not Connected):**
```json
{
  "connected": false,
  "message": "Not connected"
}
```

---

### 4. Sync Study Session
Create a study session event on Google Calendar.

**Request:**
```http
POST /integrations/google-calendar/sync-study-session
Authorization: Bearer <jwt-token>
Content-Type: application/json

{
  "title": "Advanced DSA - DP Section",
  "start_time": "2024-03-20T14:00:00Z",
  "end_time": "2024-03-20T16:00:00Z",
  "description": "Study session for Dynamic Programming",
  "study_plan_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Study session synced to Google Calendar",
  "event_id": "abc123def456"
}
```

**Parameters:**
- `title` (required): Name of the study session
- `start_time` (required): ISO 8601 datetime (UTC)
- `end_time` (required): ISO 8601 datetime (UTC)
- `description` (optional): Details about the session
- `study_plan_id` (optional): Link to study plan

**Example Usage:**
```javascript
const sessionStart = new Date();
sessionStart.setHours(14, 0, 0);

const sessionEnd = new Date(sessionStart);
sessionEnd.setHours(16, 0, 0);

const response = await fetch('/api/integrations/google-calendar/sync-study-session', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    title: 'Daily Study Session',
    start_time: sessionStart.toISOString(),
    end_time: sessionEnd.toISOString(),
    description: 'Focus on problem solving',
    study_plan_id: plan.id
  })
});
```

---

### 5. Sync Deadline
Create an all-day deadline event on Google Calendar.

**Request:**
```http
POST /integrations/google-calendar/sync-deadline
Authorization: Bearer <jwt-token>
Content-Type: application/json

{
  "title": "Complete Chapter 5: Binary Trees",
  "deadline": "2024-03-25T23:59:59Z",
  "description": "Finish watching and take quiz",
  "study_plan_id": "550e8400-e29b-41d4-a716-446655440000",
  "chapter_id": "ch-5-trees"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Deadline synced to Google Calendar",
  "event_id": "xyz789uvw123"
}
```

**Parameters:**
- `title` (required): Deadline name with emoji (e.g., "📚 Chapter 5")
- `deadline` (required): ISO 8601 datetime (UTC)
- `description` (optional): Details
- `study_plan_id` (optional): Parent study plan
- `chapter_id` (optional): Link to chapter

---

### 6. Disconnect Google Calendar
Disable Google Calendar integration.

**Request:**
```http
DELETE /integrations/google-calendar/disconnect
Authorization: Bearer <jwt-token>
```

**Response:**
```json
{
  "status": "success",
  "message": "Google Calendar disconnected"
}
```

**Notes:**
- Sets integration to inactive
- Tokens remain encrypted in DB
- Can reconnect later without authorization step

---

## Notion Integration

### 1. Setup Notion Integration
Connect a Notion database for syncing.

**Request:**
```http
POST /integrations/notion/setup
Authorization: Bearer <jwt-token>
Content-Type: application/json

{
  "api_key": "secret_abc123xyz789...",
  "workspace_id": "workspace-id-here",
  "database_id": "database-id-here"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Notion integration created successfully"
}
```

**Parameters:**
- `api_key` (required): Notion Internal Integration Token
  - Get from: https://www.notion.so/my-integrations
  - Share your database with the integration
  
- `workspace_id` (required): Your Notion workspace ID
  - Found in: Account Settings → Workspace → Workspace ID
  
- `database_id` (required): Database for syncing
  - Found in: Database URL after `/db/` or at bottom of database settings

**Example:**
```javascript
const setupNotion = async (apiKey, workspaceId, databaseId) => {
  const response = await fetch('/api/integrations/notion/setup', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      api_key: apiKey,
      workspace_id: workspaceId,
      database_id: databaseId
    })
  });
  
  return await response.json();
};
```

---

### 2. Check Notion Status
Get current Notion integration status.

**Request:**
```http
GET /integrations/notion/status
Authorization: Bearer <jwt-token>
```

**Response (Connected):**
```json
{
  "connected": true,
  "is_enabled": true,
  "sync_summaries": true,
  "sync_analytics": true,
  "last_sync_at": "2024-03-15T10:30:00Z",
  "workspace_id": "workspace-id",
  "database_id": "database-id"
}
```

**Response (Not Connected):**
```json
{
  "connected": false,
  "message": "Not connected"
}
```

---

### 3. Sync Study Plan to Notion
Create a study plan page in Notion.

**Request:**
```http
POST /integrations/notion/sync-study-plan/{study_plan_id}?include_chapters=true
Authorization: Bearer <jwt-token>
```

**URL Parameters:**
- `study_plan_id` (required): UUID of the study plan
- `include_chapters` (optional): false = only plan, true = with chapters (default: true)

**Response:**
```json
{
  "status": "success",
  "message": "Study plan synced to Notion",
  "page_id": "notion-page-uuid"
}
```

**Notion Page Properties:**
- Title: Study plan name
- Goal: Original learning goal
- Status: NotStarted
- Chapters: Number of chapters
- Type: "Study Plan"

---

### 4. Sync Chapter Summary to Notion
Create/update a chapter summary page in Notion.

**Request:**
```http
POST /integrations/notion/sync-chapter-summary/{chapter_id}
Authorization: Bearer <jwt-token>
```

**URL Parameters:**
- `chapter_id` (required): UUID of the chapter

**Response:**
```json
{
  "status": "success",
  "message": "Chapter summary synced to Notion",
  "page_id": "notion-page-uuid"
}
```

**Synced Content:**
- Title: Chapter title with 📖 emoji
- AI Summary: Auto-generated key takeaways
- Completion status: Completed/In Progress
- Parent plan: Link to parent study plan

**When Synced:**
- Auto-called when chapter is completed
- Can be manually triggered via API
- Includes AI-generated summaries

---

### 5. Sync Analytics to Notion
Create quiz performance analytics page in Notion.

**Request:**
```http
POST /integrations/notion/sync-analytics/{study_plan_id}
Authorization: Bearer <jwt-token>
```

**URL Parameters:**
- `study_plan_id` (required): UUID of the study plan

**Response:**
```json
{
  "status": "success",
  "message": "Analytics synced to Notion",
  "page_id": "notion-page-uuid"
}
```

**Synced Metrics:**
- Total quiz attempts
- Average score
- Best score
- Completion percentage
- Charts (in Notion)

---

### 6. Disconnect Notion
Disable Notion integration.

**Request:**
```http
DELETE /integrations/notion/disconnect
Authorization: Bearer <jwt-token>
```

**Response:**
```json
{
  "status": "success",
  "message": "Notion disconnected"
}
```

---

## Error Responses

All endpoints return standard error format:

**400 - Bad Request**
```json
{
  "detail": "Invalid parameters or validation failed"
}
```

**401 - Unauthorized**
```json
{
  "detail": "Missing or invalid authentication token"
}
```

**404 - Not Found**
```json
{
  "detail": "Study plan not found"
}
```

**500 - Server Error**
```json
{
  "detail": "Internal server error: [error message]"
}
```

---

## Rate Limits

| Service | Limit | Period |
|---------|-------|--------|
| Google Calendar | 1000 req/day | 24 hours |
| Notion | 3-4 req/sec | Per integration |
| LifeOS API | 100 req/min | Per user |

---

## Authentication

All endpoints require JWT token in header:
```http
Authorization: Bearer <jwt-token>
```

Get token:
```http
POST /auth/login
Content-Type: application/json

{
  "email": "student@example.com",
  "password": "password123"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## Batch Operations

### Sync All Study Plans to Notion
```javascript
const syncAllToNotion = async (studyPlans, token) => {
  const results = [];
  
  for (const plan of studyPlans) {
    const response = await fetch(
      `/api/integrations/notion/sync-study-plan/${plan.id}`,
      {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      }
    );
    
    results.push({
      planId: plan.id,
      success: response.ok,
      pageId: (await response.json()).page_id
    });
  }
  
  return results;
};
```

### Auto-Sync on Study Plan Creation
```javascript
const createAndSyncPlan = async (planData, token) => {
  // 1. Create study plan
  const planResponse = await fetch('/api/ai/generate-plan', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: JSON.stringify(planData)
  });
  const plan = await planResponse.json();
  
  // 2. Sync to Google Calendar
  const calResponse = await fetch(
    '/api/integrations/google-calendar/sync-study-session',
    {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({
        title: `Study: ${plan.title}`,
        start_time: new Date().toISOString(),
        end_time: new Date(Date.now() + 7*24*60*60*1000).toISOString(),
        study_plan_id: plan.id
      })
    }
  );
  
  // 3. Sync to Notion
  const notionResponse = await fetch(
    `/api/integrations/notion/sync-study-plan/${plan.id}`,
    {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  
  return {
    plan,
    calendarSynced: calResponse.ok,
    notionSynced: notionResponse.ok
  };
};
```

---

## Webhook Examples (Future)

```javascript
// When study plan is created
POST /webhooks/study-plan-created
{
  "plan_id": "...",
  "user_id": "...",
  "title": "...",
  "auto_sync_calendar": true,
  "auto_sync_notion": true
}

// When chapter is completed
POST /webhooks/chapter-completed
{
  "chapter_id": "...",
  "plan_id": "...",
  "user_id": "...",
  "completion_date": "2024-03-20T10:30:00Z",
  "ai_summary": "..."
}
```

---

## See Also
- [Implementation Guide](./INTEGRATION_IMPLEMENTATION_GUIDE.md)
- [Setup Checklist](./INTEGRATION_SETUP_CHECKLIST.md)
- [Google Calendar API Docs](https://developers.google.com/calendar/api)
- [Notion API Docs](https://developers.notion.com/)

Last Updated: March 17, 2026
