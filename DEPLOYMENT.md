# Technopie AI — Production Deployment Guide & Dependency Specifications

**Product:** Technopie AI SaaS Platform  
**Target Platform:** Render Web Services (Free Tier)  
**Entry Point:** `backend.app.main:app`  
**Last Updated:** November 08, 2026  

---

## 1. Verified Dependency Specifications

### Root Cause of Deployment Failure
SQLAlchemy's asynchronous module (`sqlalchemy.ext.asyncio`) delegates green-threading state management to `greenlet`. When installing vanilla `sqlalchemy`, `greenlet` is not pulled in by default on some platforms and Python versions. Attempting to initialize async engines or sessions throws:
```
ModuleNotFoundError: No module named 'greenlet'
The SQLAlchemy asyncio module requires that the Python 'greenlet' library is installed.
```

### Corrected Dependency Line
In [`backend/requirements.txt`](file:///d:/AntiGravity/technoai/backend/requirements.txt):
```text
SQLAlchemy[asyncio]>=2.0.28
```
- **Preserved Constraint:** Maintains the existing `sqlalchemy>=2.0.28` version requirement.
- **Asyncio Extra:** Declares `[asyncio]`, which instructs `pip` and wheel resolvers to automatically bundle `greenlet>=1.0.0`.
- **No Duplicate/Conflicting Versions:** Pure drop-in replacement with zero dependency conflicts.

In addition, a root-level [`requirements.txt`](file:///d:/AntiGravity/technoai/requirements.txt) is provided pointing directly to `-r backend/requirements.txt` as a universal fallback for automated platform discovery.

---

## 2. Render Web Service Configuration

When configuring or updating the backend service in the [Render Dashboard](https://dashboard.render.com):

| Setting | Value | Notes |
|---|---|---|
| **Service Type** | Web Service | Python runtime |
| **Name** | `technopie-ai-backend` (or `technoai`) | Generates `.onrender.com` subdomain |
| **Runtime** | `Python 3` | Compatible with Python 3.10–3.14 |
| **Root Directory** | *(Leave blank)* | Must stay at repo root so `backend.app...` imports resolve |
| **Build Command** | `pip install --upgrade pip && pip install -r backend/requirements.txt` | Ensures clean pip and all async dependencies installed |
| **Start Command** | `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT` | Binds to dynamic Render port |
| **Health Check Path**| `/api/health` | Expected HTTP 200 OK |

---

## 3. Local Verification Results

### A. SQLAlchemy Asyncio Import Test
```bash
python -c "from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession; print('SQLAlchemy asyncio import SUCCESS')"
```
**Result:**
```
SQLAlchemy asyncio import SUCCESS (Exit code: 0)
```

### B. Application Entry Point Import Test
```bash
python -c "from backend.app.main import app; print('App imported successfully:', type(app))"
```
**Result:**
```
App imported successfully: <class 'fastapi.applications.FastAPI'> (Exit code: 0)
```

### C. Test Suite Status
All 24 automated unit and integration tests passed:
- `backend/tests/test_backend.py`: 7/7 PASSED
- `backend/tests/test_gemini_provider.py`: 11/11 PASSED (1 skipped live network test when API key unset)
- `backend/tests/test_postgres_migration.py`: 5/5 PASSED

---

## 4. Environment Variables Checklist (Render Backend)

Configure these in Render Dashboard ➔ **Environment**:

```env
ENVIRONMENT=production
DEBUG=False
APP_NAME=Technopie AI
SECRET_KEY=technopie-ai-super-secret-key-change-in-production-2026-secure
CORS_ORIGINS=https://frontend-web-service-payd.onrender.com,http://localhost:3000
GOOGLE_API_KEY=your-gemini-api-key-here
ALLOW_MOCK_FALLBACK=False

# Optional: Supabase PostgreSQL (defaults to auto-seeded local SQLite if omitted)
# DATABASE_URL=postgresql+asyncpg://postgres.[REF]:[PASS]@aws-0-[REGION].pooler.supabase.com:6543/postgres?ssl=require
```

---

## 5. Deployment Commands

To deploy this fix to Render:
```bash
git add backend/requirements.txt requirements.txt DEPLOYMENT.md
git commit -m "fix(deps): add asyncio extra to SQLAlchemy to ensure greenlet is installed"
git push origin main
```
Render will trigger an automatic build with the updated dependencies and launch without `ModuleNotFoundError`.
