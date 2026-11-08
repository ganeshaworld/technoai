# Cloud Deployment Verification & Smoke Test Checklist
## TECHNOPIE AI — Production Launch Quality Gate

**Date:** November 08, 2026  
**Auditor:** Senior DevOps & SaaS Reliability Engineer  
**Coverage:** Pre-Deployment, Backend Boot, Database Persistence, Frontend UX & Security  

---

## 1. Pre-Deployment Readiness (Local Gate)

- [ ] **Dependency Audit:**
  - `backend/requirements.txt` includes all runtime dependencies (`fastapi`, `uvicorn`, `sqlalchemy`, `asyncpg`, `pgvector`, `alembic`, `pydantic-settings`, `cryptography`, `httpx`).
- [ ] **Git Exclusion Verification:**
  - `git status` confirms no SQLite databases (`technopie.db`, `*.db`), `.env` files, or user uploads are tracked.
- [ ] **Frontend Build Gate:**
  - `npm run build --prefix frontend` finishes with code 0 and zero TypeScript/lint errors.
- [ ] **Automated Test Suite:**
  - `pytest backend/tests/` passes 100% of non-live tests (23 passed, 1 skipped).

---

## 2. Supabase Database Gate

- [ ] **Project Active:** Supabase project is active and in `Active` status.
- [ ] **Extension Active:** `SELECT * FROM pg_extension WHERE extname = 'vector';` returns valid version.
- [ ] **IPv4 Pooler URL Formatted:** Connection URL uses port `6543` in Session Mode (`aws-0-[region].pooler.supabase.com:6543`).
- [ ] **Migrations Applied:** All 12 tables exist in Supabase schema (`users`, `user_profiles`, `conversations`, `messages`, `memories`, `tasks`, `calendar_events`, `documents`, `connected_accounts`, `automations`, `notifications`, `subscriptions`).
- [ ] **Data Preserved:** Local `backend/technopie.db` was not deleted.

---

## 3. Render Backend Service Gate

- [ ] **Build Succeeded:** Render build log ends with `Successfully installed ...` and `Build successful`.
- [ ] **Health Endpoint Responding:**
  ```bash
  curl -I https://technopie-ai-backend.onrender.com/api/health
  # Expected: HTTP/2 200 OK
  ```
- [ ] **Provider Diagnostics:**
  ```bash
  curl -s -H "Authorization: Bearer <TOKEN>" https://technopie-ai-backend.onrender.com/api/chat/provider-status
  # Expected: JSON response with default_provider: "gemini", configured: true
  ```
- [ ] **No Unhandled Errors in Logs:**
  - Logs show clean startup: `Uvicorn running on http://0.0.0.0:10000`.
  - Zero `ModuleNotFoundError` or `CannotConnectError`.

---

## 4. Render Frontend Service Gate

- [ ] **Build Succeeded:** Next.js static pages generated (4/4) with 0 build warnings.
- [ ] **Homepage Accessible:** `https://technopie-ai-frontend.onrender.com` returns HTTP 200.
- [ ] **API URL Verified:** Browser network requests target `https://technopie-ai-backend.onrender.com/api`.
- [ ] **CORS Verification:**
  - Request to `POST /api/auth/login` contains header `access-control-allow-origin: https://technopie-ai-frontend.onrender.com`.
  - Zero CORS errors in browser developer console.
- [ ] **Auto-Authentication / Login:**
  - Application dashboard successfully retrieves current user profile.
  - Sidebar shows active user name.

---

## 5. End-to-End Functional Smoke Tests

- [ ] **Chat & Cognitive Loop:**
  - Send message: *"Remember that my preferred meeting time is 10:00 AM."*
  - Verify assistant responds, categorizes intent as `memory_storage`, and commits preference.
- [ ] **Semantic Memory Recall:**
  - In a new conversation: *"What is my preferred meeting time?"*
  - Verify assistant recalls the 10:00 AM preference from PostgreSQL.
- [ ] **Task Creation:**
  - Send message: *"Create a task to review Q4 financials tomorrow."*
  - Open **Tasks** view in sidebar: Verify task appears with medium priority and tomorrow's due date.
- [ ] **Document Generation & Download:**
  - Open **Documents** view in sidebar.
  - Click **Generate Document** (DOCX / PDF).
  - Click **Download**: Verify valid binary file downloads to local machine with correct file extension.
- [ ] **Tenant Isolation (Cross-User Access):**
  - Register a second test user via `/api/auth/register`.
  - Verify second user sees empty task board and zero access to first user's documents.

---

## 6. Cold-Start & Inactivity Verification

- [ ] **Inactivity Sleep:** Allow the free tier services to sleep for 15 minutes.
- [ ] **Wake-Up Test:** Visit `https://technopie-ai-frontend.onrender.com`.
- [ ] Verify that upon initial request (~30s cold start), the application recovers cleanly and displays the dashboard without crashing.
- [ ] *(Optional)* Uptime monitor configured (e.g. UptimeRobot) pinging `GET /api/health` every 10 minutes to prevent container sleep.
