# Sample Data for Swagger Testing

This folder contains ready-to-use data for testing the Stats Service through the Swagger UI
at `http://localhost:1506/docs` (local) or the Azure URL.

---

## Step 1 — Get a JWT token

All endpoints require a Bearer token. Use one of the two options below:

### Option A — Generate one locally (Python)

Run this script if the JWT secret matches `default-secret-change-in-production`
(the default value used by the mock servers):

```python
from jose import jwt
from datetime import datetime, timedelta, timezone

token = jwt.encode(
    {
        "sub": "user-mock-01",
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=4),
    },
    "default-secret-change-in-production",
    algorithm="HS256",
)
print(token)
```

### Option B — Get it from the auth service

If auth-service is running, log in through the app and copy the token from the
`Authorization` header of any authenticated request (use browser DevTools → Network tab).

---

## Step 2 — Authorize in Swagger

1. Open the Swagger UI URL
2. Click **Authorize** (lock icon, top right)
3. Paste the token (without the `Bearer ` prefix)
4. Click **Authorize** → **Close**

---

## Step 3 — Test each endpoint

### GET /api/stats/dashboard

No parameters needed. Click **Try it out** → **Execute**.

Expected response: see `dashboard-response.json`

---

### GET /api/stats/subjects

No parameters needed. Returns a list with one entry per subject.

Expected response: see `subject-stats-response.json` (single item from the list)

---

### GET /api/stats/subjects/{subject_id}

Use one of the subject IDs available in the mock data:

| subject_id | Subject name |
|---|---|
| `sub-calculo` | Cálculo Diferencial |
| `sub-estructuras` | Estructuras de Datos |
| `sub-fisica` | Física I |

Paste the ID in the `subject_id` field and click **Execute**.

---

### GET /api/stats/gamification

No parameters needed.

Expected response: see `gamification-response.json`

---

## Available mock subject IDs (for local testing with mock servers)

```
sub-calculo
sub-estructuras
sub-fisica
```

These IDs are defined in `mocks/mock_academic_service.py`.
To use them, start both mock servers before running the stats service locally.
See `mocks/.env.local` for the required environment variable configuration.
