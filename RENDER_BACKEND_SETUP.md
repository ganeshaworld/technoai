# Render Backend Setup Guide: FastAPI Multi-Agent Engine
## TECHNOPIE AI — Production Web Service Configuration

**Product:** Technopie AI Backend  
**Hosting Platform:** Render Free Tier  
**Runtime:** Python 3.11.9  
**Application Entry Point:** `backend.app.main:app`  

---

## 1. Web Service Parameters

When creating the backend Web Service in the [Render Dashboard](https://dashboard.render.com), configure the following exact settings:

| Field | Configuration Value | Critical Notes |
|---|---|---|
| **Name** | `technopie-ai-backend` | Used to generate your onrender.com subdomain |
| **Region** | `Oregon (US West)` or `Frankfurt (EU)` | Must match your Supabase project region |
| **Branch** | `main` | Production deployment branch |
| **Root Directory** | *(Leave blank)* | **DO NOT set to `backend`!** Leave as project root `.` so that `from backend.app...` imports resolve properly. |
| **Runtime** | `Python 3` | Render manages virtualenv automatically |
| **Build Command** | `pip install --upgrade pip && pip install -r backend/requirements.txt` | Installs FastAPI, SQLAlchemy, asyncpg, pgvector, etc. |
| **Start Command** | `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT` | Binds to Render's dynamic `$PORT` |
| **Auto-Deploy** | `Yes` | Automatically triggers upon git push to `main` |
| **Plan Type** | `Free` | 512 MB RAM, 0.1 CPU |

---

## 2. Health Check & Live Probe

- **Health Check Path:** `/api/health`
- Render uses this path to determine when the application has successfully booted.
- **Expected Status Code:** `200 OK`
- **Expected Payload:**
  ```json
  {
    "status": "healthy",
    "platform": "Technopie AI",
    "environment": "production",
    "version": "1.0.0",
    "company": "Technopie Consultant Pvt. Ltd."
  }
  ```

---

## 3. Environment Variables Configuration

In Render Dashboard → **`technopie-ai-backend`** → **Environment**, add the following key-value pairs:

```env
# 1. Environment & Security
ENVIRONMENT=production
DEBUG=False
APP_NAME=Technopie AI
SECRET_KEY=generate_a_64_character_random_hex_string_here
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 2. Database Connection (Supabase IPv4 Pooler)
DATABASE_URL=postgresql+asyncpg://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?ssl=require

# 3. Foundation AI Integration
DEFAULT_AI_PROVIDER=gemini
DEFAULT_FAST_MODEL=gemini-2.5-flash
DEFAULT_REASONING_MODEL=gemini-2.5-pro
ALLOW_MOCK_FALLBACK=false
GOOGLE_API_KEY=AIzaSy...your_gemini_api_key_from_google_ai_studio
AI_REQUEST_TIMEOUT_SECONDS=30.0
AI_MAX_RETRIES=3
AI_RETRY_BACKOFF_FACTOR=1.5

# 4. CORS Origins (Whitelist your Render frontend URL)
CORS_ORIGINS=https://technopie-ai-frontend.onrender.com,http://localhost:3000

# 5. Render Python Version Pin
PYTHON_VERSION=3.11.9
```

---

## 4. Database Pre-Deploy Command (Optional / Recommended)

Render allows running a command before starting the web server. To automatically apply schema migrations on every deployment:

- Navigate to **Settings** → **Build & Deploy** → **Pre-Deploy Command**:
  ```bash
  python -m alembic upgrade head
  ```
- *Note:* The backend also executes `await init_db()` during application lifespan startup in [`backend/app/main.py`](file:///d:/AntiGravity/technoai/backend/app/main.py#L16-L20), ensuring all tables are initialized even if pre-deploy is omitted.

---

## 5. Verification & Testing

Once Render shows **"Your service is live"**:
1. **Test Health Endpoint:**
   ```bash
   curl -I https://technopie-ai-backend.onrender.com/api/health
   # Expected: HTTP/2 200
   ```
2. **Test AI Provider Status:**
   ```bash
   # Generate a test token or register via /api/auth/register
   curl -s -X POST https://technopie-ai-backend.onrender.com/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@technopie.ai", "password": "Password123!", "full_name": "Executive Admin"}'
   ```
3. **Inspect Logs:**
   Navigate to the **Logs** tab in Render to verify:
   ```
   INFO: Database connection pool initialized (pool_size=10, max_overflow=20)
   INFO: pgvector extension verified or enabled successfully.
   INFO: Application startup complete.
   INFO: Uvicorn running on http://0.0.0.0:10000
   ```

---

## 6. Troubleshooting Common Render Backend Issues

### Issue 1: `ModuleNotFoundError: No module named 'backend'`
- **Cause:** Root Directory was set to `backend` in Render settings.
- **Fix:** Clear the **Root Directory** field so it defaults to repository root `.`.

### Issue 2: `CannotConnectError: [Errno 101] Network is unreachable`
- **Cause:** Direct connection to `db.[ref].supabase.co:5432` attempted over IPv6.
- **Fix:** Use the Supabase IPv4 Pooler URL on port `6543` (`aws-0-[region].pooler.supabase.com:6543`).

### Issue 3: `502 Bad Gateway` on First Request
- **Cause:** Render free tier instance is spinning up after 15 minutes of sleep.
- **Fix:** Wait 30–40 seconds for the initial container wake-up.
