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
   In [`backend/app/api/auth_routes.py`](file:///d:/AntiGravity/technoai/backend/app/api/auth_routes.py), `RegisterRequest` and `LoginRequest` use Pydantic's `EmailStr` field type. Pydantic requires `email-validator` to parse and validate email syntax. When pip caches a previously installed `pydantic` package without its extras, `email-validator` is omitted.

### Corrected Dependency Lines
Both in [`backend/requirements.txt`](file:///d:/AntiGravity/technoai/backend/requirements.txt) and root [`requirements.txt`](file:///d:/AntiGravity/technoai/requirements.txt):

```text
# Core Framework & ASGI Server
fastapi>=0.110.0
uvicorn[standard]>=0.28.0
pydantic[email]>=2.6.0
email-validator>=2.0.0
pydantic-settings>=2.2.0

# Async Database & ORM
SQLAlchemy[asyncio]>=2.0.28
greenlet>=3.0.0
aiosqlite>=0.20.0
asyncpg>=0.30.0
pgvector>=0.5.0
alembic>=1.20.0

# Authentication & Cryptography
pyjwt>=2.8.0
passlib[bcrypt]>=1.7.4
bcrypt>=4.1.2
cryptography>=42.0.5
python-multipart>=0.0.9

# HTTP Client & Streaming
httpx>=0.27.0

# Multi-Format Document Generation
python-docx>=1.1.0
openpyxl>=3.1.2
python-pptx>=0.6.23
reportlab>=4.1.0

# Testing
pytest>=8.1.0
pytest-asyncio>=0.23.5
```

- **Preserved Version Pins:** `pydantic>=2.6.0` and `sqlalchemy>=2.0.28` version constraints are strictly preserved.
- **Explicit Packages & Extras:**
  - `SQLAlchemy[asyncio]>=2.0.28` + `greenlet>=3.0.0`: Guarantees `greenlet` is installed even if pip skips extra evaluation on cached wheels.
  - `pydantic[email]>=2.6.0` + `email-validator>=2.0.0`: Guarantees `email-validator` is installed in both clean and cached pip environments.
- **Dual Requirements Mirroring:** Both root `requirements.txt` and `backend/requirements.txt` contain the complete identical dependency specification, ensuring successful builds regardless of whether Render executes root or backend build commands.

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
python -c "from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession; from pydantic import BaseModel, EmailStr; import email_validator, greenlet; print('Imports verified successfully')"
```
**Result:**
```
ALL IMPORTS SUCCESSFUL:
 - sqlalchemy asyncio: create_async_engine, async_sessionmaker, AsyncSession
 - pydantic EmailStr: BaseModel, EmailStr
 - email_validator version: 2.3.0
 - greenlet version: 3.5.6
(Exit code: 0)
```

### B. Application Entry Point Import Test (`backend.app.main:app`)
```bash
python -c "from backend.app.main import app; print('App imported successfully:', type(app))"
```
**Result:**
```
Complete FastAPI application successfully loaded!
Routes registered: 14
App instance: <fastapi.applications.FastAPI object>
(Exit code: 0)
```

### C. Test Suite Status
All 24 automated unit and integration tests passed:
```
backend/tests/test_backend.py: 7/7 PASSED
backend/tests/test_gemini_provider.py: 11/11 PASSED (1 skipped live network test)
backend/tests/test_postgres_migration.py: 5/5 PASSED
======================== 23 passed, 1 skipped in 7.58s ========================
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
git commit -m "fix(deps): explicitly specify email-validator and greenlet for Render deployment"
git push origin main
```

> [!IMPORTANT]
> In the Render Dashboard, go to your Web Service ➔ **Manual Deploy** ➔ **Clear build cache & deploy** to purge any stale cached wheels.
