# Parent-Child Connection System — Quick Reference

## File Locations

### Backend Services
- Service Logic: `backend/app/services/parental_connection_service.py`
- API Routes: `backend/app/routes/parental_connection.py`
- Database Model: `backend/app/models/models.py` (ParentChildConnection class)

### Frontend Components
- Parent Connect Modal: `frontend/src/components/ParentConnectModal.jsx`
- OTP Verification Modal: `frontend/src/components/OtpVerificationModal.jsx`
- API Client: `frontend/src/api.js` (parental object)

### Documentation
- Full Guide: `PARENT_CHILD_CONNECTION_GUIDE.md`
- Implementation Summary: `PARENT_CHILD_CONNECTION_IMPLEMENTATION.md`
- Database Schema: `backend/parent_child_connections.sql`

---

## Quick Implementation Checklist

### Backend
- [x] Created `ParentChildConnection` ORM model
- [x] Created service layer with 6 core functions
- [x] Created API routes with 6 endpoints
- [x] Registered router in `main.py`
- [x] Connected to existing notification system
- [x] Reused productivity analytics (no duplication)

### Frontend
- [x] Created 2 modal components (320 lines total)
- [x] Updated API client with 6 functions
- [x] Full error handling and loading states
- [x] OTP input with auto-focus and paste support
- [x] Countdown timer showing expiry

### Security
- [x] OTP expires in 10 minutes
- [x] Connection expires in 30 days
- [x] Validation on every access
- [x] No access without active connection
- [x] Proper authorization checks
- [x] Auto-expiry with notifications

---

## API Endpoints (Quick Reference)

```
POST   /api/parental/request-connection         [Parent] Request connection
GET    /api/parental/connection-request/{id}    [Child]  View OTP
POST   /api/parental/verify-connection          [Parent] Verify with OTP
GET    /api/parental/child-dashboard/{id}       [Parent] View analytics
GET    /api/parental/my-connections             [Any]    List connections
POST   /api/parental/disconnect/{id}            [Any]    Disconnect
```

---

## Key Service Functions

```python
generate_otp()                          # Generate random 4-digit code
create_connection_request(db, parent_id, child_email)
get_connection_request(db, connection_id, child_id)
verify_connection(db, connection_id, parent_id, otp_code)
check_connection_validity(db, parent_id, child_id)
get_active_connections(db, user_id, as_parent)
disconnect_connection(db, connection_id, user_id)
```

---

## Frontend Component Props

### ParentConnectModal
```jsx
<ParentConnectModal
    isOpen={boolean}
    onClose={() => {}}
    onConnectionRequested={(connectionId) => {}}
/>
```

### OtpVerificationModal
```jsx
<OtpVerificationModal
    isOpen={boolean}
    onClose={() => {}}
    connectionData={{
        connection_id: string,
        parent_name: string,
        otp_code: string,
        expires_in_seconds: number
    }}
    onVerified={(result) => {}}
/>
```

---

## Database Schema (Single Table)

```sql
CREATE TABLE parent_child_connections (
    id VARCHAR(36) PRIMARY KEY,
    parent_id VARCHAR(36) FK,
    child_id VARCHAR(36) FK,
    otp_code VARCHAR(4),
    otp_created_at DATETIME,
    verified BOOLEAN DEFAULT FALSE,
    connected_at DATETIME,
    expires_at DATETIME,
    status ENUM('pending','active','expired'),
    created_at DATETIME,
    
    INDEX idx_parent_child_status (parent_id, child_id, status),
    INDEX idx_parent_child_connection (parent_id, child_id)
);
```

---

## Notification Types

| Type | Recipient | Message |
|------|-----------|---------|
| `parent_connection_request` | Child | Parent wants to connect |
| `connection_verified` | Both | Connection is active |
| `connection_expired` | Parent | Need to reconnect |

---

## Data Flow Summary

```
Parent Request
 ↓
Generate OTP → Create Notification
 ↓
Child Views OTP
 ↓
Parent Enters OTP → Verify & Activate
 ↓
Both Get Notifications
 ↓
Parent Access Analytics (30 days)
 ↓
Auto-Expiry → Both Get Notification
 ↓
Parent Must Reconnect
```

---

## Testing commands

### Test OTP Generation
```python
from app.services.parental_connection_service import generate_otp
otp = generate_otp()  # Returns "1234"
```

### Test Connection Creation
```bash
curl -X POST http://localhost:8000/api/parental/request-connection \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"child_email":"test@example.com"}'
```

### Test Analytics Access
```bash
curl -X GET http://localhost:8000/api/parental/child-dashboard/{child_id} \
  -H "Authorization: Bearer {parent_token}"
```

---

## Validation Rules

| Field | Rule | Error Message |
|-------|------|---------------|
| child_email | Must exist | "Child user not found" |
| otp_code | Must be 4 digits | "Invalid OTP" |
| otp_age | Must be < 10 min | "OTP has expired" |
| connection_status | Must be 'active' | "No active connection" |
| expires_at | Must be > now() | "Connection has expired" |

---

## Performance Notes

- OTP validation: **O(1)** — direct string comparison
- Connection lookup: **O(1)** — indexed query
- List connections: **O(n)** — n = active connections (< 5 typically)
- Analytics reuse: **No overhead** — reuses existing optimized queries

---

## Security Checklist (✅ All Done)

- [x] OTP random and 4 digits
- [x] OTP expires in 10 minutes
- [x] Connection expires in 30 days
- [x] Only verified connections allow access
- [x] Expiry checked on every access
- [x] Proper authorization (JWT required)
- [x] No analytics duplication
- [x] Notifications on key events
- [x] Either party can disconnect

---

## Integration Points

1. **Navbar Notifications** — Display new notification types
2. **Parent Settings Page** — Add "Connect to Child" button
3. **Child Notifications** — Display OTP modals
4. **Dashboard** — Add "Child Analytics" section for parents
5. **Settings** — Add "Connected Parents/Children" list

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| OTP doesn't show in notification | Check notification service is working |
| Connection not created | Verify child email exists in users table |
| Analytics show 401 error | Check connection status and expiry |
| OTP expires too fast | Check system time is correct |
| Notifications not appearing | Check notification system integration |

---

## Next Steps After Deployment

1. Test in staging environment
2. Add to parent settings page UI
3. Test complete 4-step flow with real accounts
4. Monitor connection auto-expiry emails
5. Gather user feedback on modal UX
6. Consider enhancement options (email OTP, multi-parent, etc.)

---

## Version
- Created: March 13, 2026
- System: Polaris / LifeOS
- Feature: Parent-Child Connection with OTP
- Status: ✅ Ready for deployment
