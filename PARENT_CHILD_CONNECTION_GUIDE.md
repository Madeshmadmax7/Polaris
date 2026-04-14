# Parent-Child Connection System — Complete Implementation Guide

## Overview

This document provides a complete guide to the Parent-Child Connection System using OTP verification.

**Key Features:**
- Parents connect to children using email + OTP verification
- Connections are verified and valid for 30 days
- Parents can view child's analytics dashboard (productivity score, domain breakdown, YouTube videos)
- Automatic expiry notifications
- Easy disconnect functionality

---

## Architecture

### Database Schema

**New Table: `parent_child_connections`**

```sql
CREATE TABLE parent_child_connections (
    id VARCHAR(36) PRIMARY KEY,
    parent_id VARCHAR(36) NOT NULL,
    child_id VARCHAR(36) NOT NULL,
    otp_code VARCHAR(4) NOT NULL,
    otp_created_at DATETIME NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    connected_at DATETIME,
    expires_at DATETIME,
    status ENUM('pending','active','expired') DEFAULT 'pending',
    created_at DATETIME,
    
    FOREIGN KEY (parent_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (child_id) REFERENCES users(id) ON DELETE CASCADE,
    
    INDEX idx_parent_child_status (parent_id, child_id, status),
    INDEX idx_parent_child_connection (parent_id, child_id)
);
```

### ORM Model

**File:** `backend/app/models/models.py`

```python
class ParentChildConnection(Base):
    __tablename__ = "parent_child_connections"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    parent_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    child_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    otp_code = Column(String(4), nullable=False)
    otp_created_at = Column(DateTime, default=utcnow, nullable=False)
    verified = Column(Boolean, default=False)
    connected_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="pending")  # 'pending' | 'active' | 'expired'
    created_at = Column(DateTime, default=utcnow)

    parent = relationship("User", foreign_keys=[parent_id])
    child = relationship("User", foreign_keys=[child_id])
```

---

## API Endpoints

### 1. Request Connection
**Endpoint:** `POST /api/parental/request-connection`

**Authentication:** Required (Parent)

**Request Body:**
```json
{
  "child_email": "child@example.com"
}
```

**Response (Success):**
```json
{
  "success": true,
  "connection_id": "uuid-here",
  "message": "OTP sent to child's notification panel"
}
```

**Response (Error):**
```json
{
  "detail": "Child user not found" | "Connection already exists or pending verification"
}
```

**In Parental Connection Service:**
- Generates random 4-digit OTP
- Creates `ParentChildConnection` record with `status='pending'`
- Creates notification for child type: `"parent_connection_request"`
- Notification data includes `parent_id` and `connection_id`

---

### 2. Get Connection Request (Child View)
**Endpoint:** `GET /api/parental/connection-request/{connection_id}`

**Authentication:** Required (Child)

**Response (Success):**
```json
{
  "success": true,
  "parent_name": "John Doe",
  "otp_code": "1234",
  "expires_in_seconds": 580
}
```

**Response (Error):**
```json
{
  "detail": "OTP has expired. Request a new connection."
}
```

**Security Logic:**
- Validates OTP age (must be < 10 minutes)
- Only returns if requested by the child user
- Auto-expires the connection if OTP is stale

---

### 3. Verify Connection (Parent Enters OTP)
**Endpoint:** `POST /api/parental/verify-connection`

**Authentication:** Required (Parent)

**Request Body:**
```json
{
  "connection_id": "uuid-here",
  "otp_code": "1234"
}
```

**Response (Success):**
```json
{
  "success": true,
  "verified": true,
  "child_id": "child-uuid",
  "child_name": "Jane Doe",
  "expires_at": "2026-04-13T12:34:56Z"
}
```

**Response (Error):**
```json
{
  "detail": "Invalid OTP" | "OTP has expired. Request a new connection."
}
```

**In Service:**
- Validates OTP matches
- Validates OTP age (< 10 minutes)
- Updates record: `status='active'`, `verified=true`, `connected_at=now()`, `expires_at=now()+30days`
- Creates notifications for both parent and child

---

### 4. View Child Analytics
**Endpoint:** `GET /api/parental/child-dashboard/{child_id}`

**Authentication:** Required (Parent)

**Response (Success):**
```json
{
  "success": true,
  "child_id": "child-uuid",
  "child_name": "Jane Doe",
  "trend": {
    "scores": [
      {
        "date": "2026-03-01",
        "productivity_score": 75,
        "focus_factor": 0.89,
        "total_active_minutes": 120,
        "productive_minutes": 90,
        "neutral_minutes": 24,
        "distracting_minutes": 6,
        "tab_switches": 12,
        "quiz_average": 82.5,
        "top_domains": ["github.com", "leetcode.com", ...]
      },
      ...
    ],
    "average_score": 72.5,
    "trend": "improving" | "declining" | "stable"
  },
  "today": {
    "productivity_score": 78,
    "focus_factor": 0.91,
    ...
  }
}
```

**Response (Error):**
```json
{
  "detail": "No active connection or connection has expired"
}
```

**Security Logic:**
- Checks `check_connection_validity()` — validates:
  - Connection exists
  - `status='active'`
  - `expires_at > now()`
- Reuses existing `get_productivity_trend()` and `get_daily_summary()` from productivity service
- **NO duplication of analytics logic**

---

### 5. List My Connections
**Endpoint:** `GET /api/parental/my-connections`

**Authentication:** Required

**Response (Parent):**
```json
{
  "success": true,
  "role": "parent",
  "connections": [
    {
      "connection_id": "uuid",
      "user_id": "child-uuid",
      "username": "jane_doe",
      "email": "jane@example.com",
      "role": "child",
      "connected_at": "2026-03-13T10:00:00Z",
      "expires_at": "2026-04-13T10:00:00Z",
      "expires_in_days": 30
    }
  ]
}
```

**Response (Child):**
```json
{
  "success": true,
  "role": "student",
  "connections": [
    {
      "connection_id": "uuid",
      "user_id": "parent-uuid",
      "username": "john_doe",
      "email": "john@example.com",
      "role": "parent",
      "connected_at": "2026-03-13T10:00:00Z",
      "expires_at": "2026-04-13T10:00:00Z",
      "expires_in_days": 30
    }
  ]
}
```

---

### 6. Disconnect Connection
**Endpoint:** `POST /api/parental/disconnect/{connection_id}`

**Authentication:** Required (Parent or Child)

**Response (Success):**
```json
{
  "success": true,
  "message": "Connection disconnected"
}
```

**Response (Error):**
```json
{
  "detail": "Unauthorized" | "Connection not found"
}
```

**Logic:**
- Either parent or child can disconnect
- Sets `status='expired'` and `expires_at=now()`
- Prevents further analytics access

---

## Frontend Integration

### Key Components

**1. ParentConnectModal.jsx**
- Modal to enter child's email
- Sends connection request
- Shows success message with connection ID
- Props: `isOpen`, `onClose`, `onConnectionRequested`

**2. OtpVerificationModal.jsx**
- 4-digit OTP input boxes with auto-focus
- Paste support (automatically fills all boxes)
- Countdown timer showing OTP expiry
- Sends verification request
- Props: `isOpen`, `onClose`, `connectionData`, `onVerified`

### API Client Functions

```javascript
// In frontend/src/api.js

export const parental = {
    // ... existing functions ...
    
    // OTP-based connection
    requestConnection: (childEmail) => request('/parental/request-connection', {
        method: 'POST',
        body: JSON.stringify({ child_email: childEmail })
    }),
    
    getConnectionRequest: (connectionId) => request(`/parental/connection-request/${connectionId}`),
    
    verifyConnection: (connectionId, otpCode) => request('/parental/verify-connection', {
        method: 'POST',
        body: JSON.stringify({ connection_id: connectionId, otp_code: otpCode })
    }),
    
    getChildDashboard: (childId) => request(`/parental/child-dashboard/${childId}`),
    
    getMyConnections: () => request('/parental/my-connections'),
    
    disconnect: (connectionId) => request(`/parental/disconnect/${connectionId}`, { 
        method: 'POST' 
    }),
};
```

### Usage Example

```javascript
import ParentConnectModal from './components/ParentConnectModal';
import OtpVerificationModal from './components/OtpVerificationModal';
import { parental } from './api';

export default function ParentSettings() {
    const [showConnectModal, setShowConnectModal] = useState(false);
    const [showOtpModal, setShowOtpModal] = useState(false);
    const [connectionData, setConnectionData] = useState(null);
    const [connections, setConnections] = useState([]);

    // Load active connections
    useEffect(() => {
        parental.getMyConnections().then(data => {
            setConnections(data.connections);
        });
    }, []);

    // Handle connection request
    const handleConnectionRequested = (connectionId) => {
        setShowConnectModal(false);
        setConnectionData({ connection_id: connectionId });
        
        // Get OTP details for modal
        parental.getConnectionRequest(connectionId).then(data => {
            setConnectionData({ ...data, connection_id: connectionId });
            setShowOtpModal(true);
        });
    };

    // Handle verification
    const handleVerified = (result) => {
        setShowOtpModal(false);
        // Refresh connections list
        parental.getMyConnections().then(data => {
            setConnections(data.connections);
        });
    };

    return (
        <>
            <button onClick={() => setShowConnectModal(true)}>
                Connect to Child
            </button>

            <ParentConnectModal
                isOpen={showConnectModal}
                onClose={() => setShowConnectModal(false)}
                onConnectionRequested={handleConnectionRequested}
            />

            <OtpVerificationModal
                isOpen={showOtpModal}
                onClose={() => setShowOtpModal(false)}
                connectionData={connectionData}
                onVerified={handleVerified}
            />
        </>
    );
}
```

---

## Notification Types

The system uses the existing notification system with new types:

### For Children
**Type:** `parent_connection_request`
```json
{
  "type": "parent_connection_request",
  "title": "Connection Request",
  "message": "A parent wants to connect to your account. Check the notification for OTP.",
  "data": {
    "parent_id": "uuid",
    "connection_id": "uuid"
  }
}
```

**Type:** `connection_verified`
```json
{
  "type": "connection_verified",
  "title": "Parent Connected",
  "message": "A parent has successfully verified connection to your account.",
  "data": {
    "parent_id": "uuid"
  }
}
```

### For Parents
**Type:** `connection_verified`
```json
{
  "type": "connection_verified",
  "title": "Connection Established",
  "message": "Your connection has been verified. You can now view analytics.",
  "data": {
    "child_id": "uuid"
  }
}
```

**Type:** `connection_expired`
```json
{
  "type": "connection_expired",
  "title": "Connection Expired",
  "message": "Your connection with this child has expired. Please reconnect.",
  "data": {
    "child_id": "uuid"
  }
}
```

---

## Security Rules Implemented

✅ OTP expires in 10 minutes
✅ Parent cannot access child analytics without verified connection
✅ Child email must exist in database
✅ Only one active connection per parent-child pair (checked in `create_connection_request`)
✅ OTP must be exactly 4 digits (random generation + validation)
✅ Connection auto-expires after 30 days
✅ Expiry is checked on every analytics access (and notification sent)
✅ Either party can disconnect at any time

---

## Data Flow — Step by Step

### Parent Initiates Connection

```
Parent enters child's email in UI
  ↓
POST /api/parental/request-connection
  ↓
Backend:
  1. Find child by email
  2. Check for existing active/pending connections
  3. Generate 4-digit OTP
  4. Create ParentChildConnection (status='pending')
  5. Create notification for child
  ↓
Return connection_id to parent
```

### Child Sees Notification

```
Child receives notification (parent_connection_request)
  ↓
Child clicks on notification to view OTP
  ↓
GET /api/parental/connection-request/{connection_id}
  ↓
Backend:
  1. Check OTP age (< 10 minutes)
  2. Return parent_name + otp_code + countdown
  ↓
Child sees 4-digit OTP on screen
```

### Parent Enters OTP

```
Parent receives notification or uses modal
  ↓
Parent enters 4-digit OTP using 4-box input
  ↓
POST /api/parental/verify-connection
  ↓
Backend:
  1. Validate OTP matches (case-sensitive)
  2. Validate OTP age (< 10 minutes)
  3. Update record: status='active', verified=true, expires_at=now()+30 days
  4. Create notifications for both parties
  ↓
Return success + child name
```

### Parent Views Child Analytics

```
Parent navigates to "Child Analytics" page
  ↓
GET /api/parental/child-dashboard/{child_id}
  ↓
Backend:
  1. Check child_id is in active verified connections
  2. Check expires_at > now()
  3. Fetch productivity trend data (reuses existing service)
  4. Fetch today's summary (reuses existing service)
  ↓
Return analytics dashboard data
  ↓
Frontend renders:
  - Productivity score chart
  - Focus factor
  - Domain breakdown
  - YouTube videos watched
```

### Auto Expiry

```
Every time parent tries to access analytics after 30 days:
  ↓
check_connection_validity() detects expiry
  ↓
1. Update status='expired'
2. Create notification: "Connection expired. Please reconnect."
  ↓
Return 401 error to frontend
```

---

## File Structure

### Backend Files Created
```
backend/app/
├── models/models.py (MODIFIED - added ParentChildConnection)
├── services/
│   └── parental_connection_service.py (NEW)
├── routes/
│   └── parental_connection.py (NEW)
└── main.py (MODIFIED - added router)
```

### Frontend Files Created
```
frontend/src/
├── components/
│   ├── ParentConnectModal.jsx (NEW)
│   └── OtpVerificationModal.jsx (NEW)
└── api.js (MODIFIED - added parental connection functions)
```

---

## Testing Checklist

- [ ] Parent can request connection with valid child email
- [ ] Parent gets error if child email doesn't exist
- [ ] Child receives notification with correct data
- [ ] Child can view OTP code from notification
- [ ] OTP expires after 10 minutes
- [ ] Parent can enter OTP and verify connection
- [ ] Invalid OTP shows error
- [ ] Parent can access child analytics after verification
- [ ] Parent gets error if accessing before verification
- [ ] Connection expires after 30 days
- [ ] Parent receives expiry notification
- [ ] Either party can disconnect
- [ ] Cannot view analytics after disconnection
- [ ] Only one active connection per parent-child pair

---

## Future Enhancements

1. **Email Verification**: Send OTP via email instead of inapp notification
2. **Biometric Verification**: Add fingerprint/face verification for extra security
3. **Analytics Export**: Let parents export child analytics as PDF
4. **Multiple Parents**: Allow multiple parents to connect to one child
5. **Time-based Access**: Parents setup time windows for analytics access
6. **Alert Thresholds**: Notify parent if productivity score drops below threshold
7. **Weekly Reports**: Auto-send weekly summary email to parents
