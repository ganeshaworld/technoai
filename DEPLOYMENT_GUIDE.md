# TECHNOPIE AI — MASTER CLOUD DEPLOYMENT GUIDE
## Free Cloud Testing Architecture: GitHub + Render + Supabase + Google Gemini

**Author:** Senior DevOps & Cloud Infrastructure Engineer  
**Product:** Technopie AI — "Your AI. Your Assistant. Your Productivity."  
**Target Environment:** 100% Free Testing Cloud Tier  
**Last Updated:** November 08, 2026  

---

## 1. System Architecture & Topology

The production architecture decouples the frontend, backend, database, and AI foundation models into independent cloud services connected over TLS:

```mermaid
flowchart TD
    Client["Client Web Browser<br/>(Desktop / Mobile)"] -->|HTTPS| Frontend["Render Free Web Service<br/>Next.js 14 App Router<br/>(technopie-frontend.onrender.com)"]
    Frontend -->|REST / Bearer JWT| Backend["Render Free Web Service<br/>FastAPI Async Engine<br/>(technopie-backend.onrender.com)"]
    Backend -->|IPv4 Port 6543 / SSL| Supabase["Supabase Free PostgreSQL + pgvector<br/>aws-0-[region].pooler.supabase.com<br/>(Session Pooler)"]
    Backend -->|HTTPS API Key| Gemini["Google Generative AI<br/>Gemini 2.5 Flash / Pro<br/>(generativelanguage.googleapis.com)"]
    Backend -->|OAuth 2.0 PKCE| GoogleCloud["Google Workspace API<br/>Gmail & Calendar Read-Only<br/>(accounts.google.com)"]
```

---

## 2. Deployment Sequence & Prerequisites

| Step | Platform | Service | Output / Artifact Needed |
|---|---|---|---|
| **Step 1** | **GitHub** | Private Repository | Git clone/push URL (`git@github.com:...`) |
| **Step 2** | **Supabase** | Free PostgreSQL | IPv4 Connection Pooler URL (`DATABASE_URL`), `vector` extension |
| **Step 3** | **Google AI Studio** | Gemini Foundation API | `GOOGLE_API_KEY` |
| **Step 4** | **Render** | Backend Web Service | `https://technopie-backend.onrender.com` URL |
| **Step 5** | **Render** | Frontend Web Service | `https://technopie-frontend.onrender.com` URL |
| **Step 6** | **Render (Backend)** | Update `CORS_ORIGINS` | Whitelist the frontend Render URL |
| **Step 7** | **Google Cloud Console** | Update OAuth Redirects | Authorize production frontend origin and callback URL |

---

## 3. Step 1: GitHub Private Repository Setup

1. Open [GitHub](https://github.com/new) and create a **New Repository**.
   - **Repository Name:** `technopie-ai` (or your preferred name)
   - **Visibility:** **Private** (Crucial: keeps architectural documentation private)
   - **Do NOT** check "Add a README", "Add .gitignore", or "Choose a license" (all exist locally).
2. On your local terminal, link the remote repository:
   ```bash
   git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/technopie-ai.git
   git branch -M main
   git push -u origin main
   ```
3. Verify that sensitive files are excluded:
   - Check that `backend/technopie.db`, `.env`, `backend/backups/`, and `backend/uploads/` are **not** in GitHub.

---

## 4. Step 2: Supabase Free PostgreSQL Provisioning

1. Log into [Supabase Dashboard](https://supabase.com/dashboard) and click **New Project**.
   - **Name:** `technopie-ai-db`
   - **Database Password:** Store securely (e.g. 16+ characters).
   - **Region:** Select the same region you plan to use on Render (e.g., `us-west-1` or `eu-central-1`).
2. Enable the `pgvector` extension:
   - Navigate to **SQL Editor** in the left sidebar.
   - Run the following query:
     ```sql
     CREATE EXTENSION IF NOT EXISTS vector;
     ```
3. Locate the **IPv4 Connection Pooler URL** (MANDATORY FOR RENDER FREE TIER):
   - Navigate to **Project Settings** → **Database** → **Connection pooling**.
   - Select **Mode: Session** and copy the URI on port `6543`.
   - Format:
     ```
     postgresql+asyncpg://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?ssl=require
     ```
   > ⚠️ **DevOps Note:** Direct connections to `db.[ref].supabase.co:5432` use IPv6. Render Free Tier does not support outbound IPv6. You must use the pooler on port `6543`.

---

## 5. Step 3: Render Backend Web Service Setup

For exhaustive instructions, see [RENDER_BACKEND_SETUP.md](file:///d:/AntiGravity/technoai/RENDER_BACKEND_SETUP.md).

1. In [Render Dashboard](https://dashboard.render.com), click **New +** → **Web Service**.
2. Connect your GitHub repository `technopie-ai`.
3. Configure the service:
   - **Name:** `technopie-ai-backend`
   - **Region:** Match Supabase region.
   - **Branch:** `main`
   - **Root Directory:** *(Leave blank — defaults to project root)*
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install --upgrade pip && pip install -r backend/requirements.txt`
   - **Start Command:** `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** `Free`
4. Expand **Advanced** → **Add Environment Variables**:
   - `ENVIRONMENT`: `production`
   - `DEBUG`: `False`
   - `SECRET_KEY`: *(Generate via `openssl rand -hex 32`)*
   - `DATABASE_URL`: *(Your Supabase IPv4 Pooler URL from Step 2)*
   - `DEFAULT_AI_PROVIDER`: `gemini`
   - `GOOGLE_API_KEY`: *(Your Google Gemini API Key)*
   - `ALLOW_MOCK_FALLBACK`: `false`
   - `CORS_ORIGINS`: `http://localhost:3000` *(Will be updated after frontend creation)*
   - `PYTHON_VERSION`: `3.11.9`
5. Set **Health Check Path** to `/api/health`.
6. Click **Create Web Service**. Wait for the build to finish and verify `{"status": "healthy"}` at `https://technopie-ai-backend.onrender.com/api/health`.

---

## 6. Step 4: Render Frontend Web Service Setup

For exhaustive instructions, see [RENDER_FRONTEND_SETUP.md](file:///d:/AntiGravity/technoai/RENDER_FRONTEND_SETUP.md).

1. In Render Dashboard, click **New +** → **Web Service**.
2. Connect the same `technopie-ai` GitHub repository.
3. Configure the service:
   - **Name:** `technopie-ai-frontend`
   - **Region:** Match backend.
   - **Branch:** `main`
   - **Root Directory:** `frontend`
   - **Runtime:** `Node`
   - **Build Command:** `npm install && npm run build`
   - **Start Command:** `npm run start`
   - **Plan:** `Free`
4. Add Environment Variables:
   - `NEXT_PUBLIC_API_URL`: `https://technopie-ai-backend.onrender.com/api`
   - `NODE_VERSION`: `20.12.2`
5. Click **Create Web Service**. Wait for the build to finish.
6. Copy your frontend URL: e.g. `https://technopie-ai-frontend.onrender.com`.

---

## 7. Step 5: Post-Deployment Interconnection & CORS

1. Return to the **Backend Web Service** on Render → **Environment**.
2. Update `CORS_ORIGINS` to include your new production frontend domain:
   ```
   CORS_ORIGINS=https://technopie-ai-frontend.onrender.com,http://localhost:3000
   ```
3. Save changes. Render will automatically redeploy the backend with the updated CORS policy.

---

## 8. Managing Render Free Tier Constraints

| Free Tier Constraint | Impact | Production Mitigation |
|---|---|---|
| **15-Minute Inactivity Sleep** | Web services sleep after 15 minutes of zero traffic. First incoming request takes 30–50s to cold start. | 1. Use a free uptime monitor (e.g. UptimeRobot or Cron-job.org) calling `GET /api/health` every 10 minutes.<br/>2. Frontend displays connection state during wake-up. |
| **Ephemeral Disk** | Files written to `backend/uploads/` or `backend/generated_docs/` are lost when the container sleeps or redeploys. | Generated documents can be re-generated on the fly. For persistent storage, integrate Supabase Storage bucket or AWS S3. |
| **512 MB RAM Limit** | Memory spikes during heavy document rendering could cause OOM restart. | FastAPI streams responses and avoids loading large binaries in memory. |
