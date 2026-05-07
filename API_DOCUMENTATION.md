# EduCore API Documentation

This document describes the available API endpoints in the EduCore Multi-tenant School Management SaaS.

## Authentication

All API requests (except public endpoints) require authentication. EduCore uses standard Django Session or Token authentication. For mobile/external clients, ensure the `Authorization` header or session cookie is provided.

**Base URL**: `https://<subdomain>.educore.com/api/` (or your local/production domain)

---

## 1. Mobile Sync API

These endpoints are designed for the mobile app to sync data for offline use.

### `GET /api/initial-sync/`
Fetches all necessary data for the school context for initial setup on a mobile device.

- **Permissions**: IsAuthenticated
- **Response**:
  ```json
  {
    "school": { ... },
    "academic_years": [ ... ],
    "class_levels": [ ... ],
    "subjects": [ ... ],
    "class_sections": [ ... ],
    "students": [ ... ],
    "terms": [ ... ],
    "grade_scales": [ ... ],
    "announcements": [ ... ],
    "teachers": [ ... ],
    "attendance_sessions": [ ... ]
  }
  ```

### `POST /api/sync/`
Synchronizes local changes from the mobile device to the server using a batch operations approach.

- **Permissions**: IsAuthenticated
- **Request Body**:
  ```json
  {
    "operations": [
      {
        "model": "student",
        "type": "update",
        "data": { "id": "uuid", "first_name": "John", "updated_at": "..." }
      },
      {
        "model": "attendance_record",
        "type": "create",
        "data": { ... }
      }
    ]
  }
  ```
- **Response**: A list of results for each operation, including conflict resolution data if the server has newer records.

---

## 2. Analytics API

Endpoints used for dashboard visualizations.

### `GET /analytics/api/attendance/`
Fetches attendance percentages for the last 7 days.

- **Permissions**: IsAuthenticated
- **Response**:
  ```json
  {
    "data": [
      { "date": "2026-05-01", "pct": 95.5, "present": 191, "total": 200 },
      ...
    ]
  }
  ```

### `GET /analytics/api/fees/`
Fetches fee collection summary for the last 6 months.

- **Permissions**: IsAuthenticated
- **Response**:
  ```json
  {
    "data": [
      { "month": "2026-01", "collected": 5000.00 },
      ...
    ]
  }
  ```

---

## How to Use the APIs

### Python (using `requests`)
```python
import requests

# Example: Get initial sync data
url = "https://demo.educore.com/api/initial-sync/"
headers = {"Authorization": "Token your_token_here"}
response = requests.get(url, headers=headers)
data = response.json()
```

### JavaScript (Fetch API)
```javascript
// Example: Post sync operations
const syncData = {
  operations: [
    { model: 'attendance_record', type: 'create', data: { student: 1, status: 'present' } }
  ]
};

fetch('https://demo.educore.com/api/sync/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCookie('csrftoken') // For session auth
  },
  body: JSON.stringify(syncData)
})
.then(response => response.json())
.then(data => console.log(data));
```

## Multi-tenancy Note
Always ensure you are hitting the correct subdomain (e.g., `schoolname.educore.com`). The `SchoolMiddleware` uses the host header to determine which school's data to serve.
