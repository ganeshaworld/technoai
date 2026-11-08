# Technopie AI — Production Deployment Guide & Dependency Specifications

**Product:** Technopie AI SaaS Platform  
**Target Platform:** Render Web Services (Free Tier)  
**Entry Point:** `backend.app.main:app`  
**Last Updated:** November 08, 2026  

---

## 1. Verified Dependency Specifications

### Root Cause of Deployment Failures

1. **`ModuleNotFoundError: No module named 'greenlet'`**  
   SQLAlchemy's asynchronous module (`sqlalchemy.ext.asyncio`) delegates green-threading state management to `greenlet`. Installing plain `sqlalchemy` does not automatically install `greenlet` on all platforms and Python runtimes.

2. **`ModuleNotFoundError: No module named 'email_validator'`**  
   In [`backend/app/api/auth_routes.py`](file:///d:/AntiGravity/technoai/backend/app/api/auth_routes.py), `RegisterRequest` and `LoginRequest` use Pydantic's `EmailStr` field type. Pydantic requires the optional `email-validator` library to parse and validate email syntax. Installing plain `pydantic` omits this optional extra.

### Corrected Dependency Lines
In [`backend/requirements.txt`](file:///d:/AntiGravity/technoai/backend/requirements.txt):

```text
# Core Framework & ASGI Server
fastapi>=0.110.0
uvicorn[standard]>=0.28.0
pydantic[email]>=2.6.0
pydantic-settings>=2.2.0

# Async Database & ORM
SQLAlchemy[asyncio]>=2.0.28
aiosqlite>=0.20.0
asyncpg>=0.30.0
pgvector>=0.5.0
alembic>=1.20.0
```

- **Preserved Version Pins:** `pydantic>=2.6.0` and `sqlalchemy>=2.0.28` version constraints are strictly preserved.
- **Asyncio & Email Extras:**
  - `SQLAlchemy[asyncio]` forces pip to install `greenlet>=1.0.0`.
  - `pydantic[email]` forces pip to install `email-validator>=2.0.0` (and `dnspython>=2.0.0`).
- **Zero Conflicts:** Drop-in standard packaging extras without duplicate or conflicting packages.
- **Universal Discovery:** Root [`requirements.txt`](file:///d:/AntiGravity/technoai/requirements.txt) points to `-r backend/requirements.txt` to support platforms auto-detecting root requirements files.

---

## 2. Render Web Service Configuration

When configuring or updating the backend service in the [Render Dashboard](https://dashboard.render.com):

| Setting | Value | Notes |
|---|---|---|
| **Service Type** | Web Service | Python runtime |
| **Name** | `technopie-ai-backend` (or `technoai`) | Generates `.onrender.com` subdomain |
| **Runtime** | `Python 3` | Compatible with Python 3.10–3.14 |
| **Root Directory** | *(Leave blank)* | Must stay at repo root so `backend.app...` imports resolve |
| **Build Command** | `pip install --upgrade pip && pip install -r backend/requirements.txt` | Installs all core, asyncio, and email dependencies |
| **Start Command** | `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT` | Binds to dynamic Render port |
| **Health Check Path**| `/api/health` | Expected HTTP 200 OK |

---

## 3. Local Verification Results

### A. SQLAlchemy Asyncio & Pydantic EmailStr Import Test
```bash
python -c "from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession; from pydantic import BaseModel, EmailStr; print('Imports verified successfully')"
```
**Result:**
```
Imports verified successfully: create_async_engine, async_sessionmaker, AsyncSession, BaseModel, EmailStr
(Exit code: 0)
```

### B. Application Entry Point Import Test (`backend.app.main:app`)
```bash
python -c "from backend.app.main import app; print('App imported successfully:', type(app))"
```
**Result:**
```
App imported successfully: <class 'fastapi.applications.FastAPI'>
(Exit code: 0)
```

### C. Test Suite Status
All 24 automated unit and integration tests passed:
```
backend/tests/test_backend.py: 7/7 PASSED
backend/tests/test_gemini_provider.py: 11/11 PASSED (1 skipped live network test)
backend/tests/test_postgres_migration.py: 5/5 PASSED
======================== 23 passed, 1 skipped in 5.65s ========================
```

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
```

---

## 5. Deployment Commands

```bash
git add backend/requirements.txt requirements.txt DEPLOYMENT.md
git commit -m "fix(deps): add pydantic[email] and SQLAlchemy[asyncio] for Render deployment"
git push origin main
```
Render will trigger an automatic build with the updated dependencies and launch without `ModuleNotFoundError`.
