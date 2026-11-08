# Supabase Setup Guide: Managed PostgreSQL + pgvector
## TECHNOPIE AI — Cloud Database Configuration & Zero-Data-Loss Migration

**Database:** Managed PostgreSQL 15+  
**Extensions:** `pgvector` (Vector Embeddings)  
**ORM / Driver:** SQLAlchemy 2.0 + `asyncpg`  
**Migration Engine:** Alembic (Revision: `112f8b46fc68`)  

---

## 1. Create a Supabase Project

1. Log into [Supabase](https://supabase.com/dashboard) and click **New Project**.
2. Fill in the project parameters:
   - **Name:** `technopie-ai-db`
   - **Database Password:** Choose a strong password and save it securely.
   - **Region:** Select the same region as Render (e.g. `US West (Oregon)` or `EU Central (Frankfurt)`).
   - **Pricing Plan:** Free Tier.
3. Wait 1–2 minutes for the database cluster to finish provisioning.

---

## 2. Enable pgvector Extension

1. In the Supabase left navigation panel, click **SQL Editor**.
2. Click **New Query** and execute:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. Click **Run**.
4. Confirm success:
   ```sql
   SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';
   ```
   *Expected output: `vector | 0.5.x` or higher.*

---

## 3. Obtain the Mandatory IPv4 Connection Pooler URL

> 🚨 **CRITICAL DEVOPS NOTICE (Render Free Tier Compatibility):**
> Render Free Web Services **do not support outbound IPv6**.
> Direct connections to Supabase (`db.[ref].supabase.co:5432`) use IPv6 and **will fail to connect from Render**.
> You **MUST** use the Supabase Connection Pooler on port **`6543`** which provides an IPv4 endpoint.

1. In the Supabase Dashboard, go to **Project Settings** (gear icon) → **Database**.
2. Scroll to the **Connection pooling** section.
3. Configure:
   - **Mode:** `Session` (Session mode is required for prepared statements in asyncpg).
   - **Port:** `6543`
4. Copy the URI string and adapt the protocol for SQLAlchemy asyncpg:
   - Original Supabase URI:
     `postgresql://postgres.[REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres`
   - **Required SQLAlchemy asyncpg Format:**
     ```
     postgresql+asyncpg://postgres.[REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?ssl=require
     ```
5. Test this connection string as the `DATABASE_URL` environment variable on Render.

---

## 4. Run Schema Migrations Against Supabase

You can initialize the Supabase schema using either of the following methods:

### Method A: Automated Startup Lifespan
When the backend starts up on Render, [`backend/app/main.py`](file:///d:/AntiGravity/technoai/backend/app/main.py#L16-L20) runs `await init_db()`, which automatically creates all 12 tables and registers the vector extension if not present.

### Method B: Alembic CLI (Manual / Pre-Deploy)
To run version-controlled migrations explicitly from your local machine targeting Supabase:

```powershell
# Set DATABASE_URL to your Supabase pooler URL:
$env:DATABASE_URL="postgresql+asyncpg://postgres.[REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?ssl=require"

# Apply all migrations:
Set-Location backend
..\.venv\Scripts\alembic.exe upgrade head
```

---

## 5. Safe Zero-Data-Loss Migration from SQLite to Supabase

To transfer your existing local data (36 users, 21 profiles, 53 conversations, 121 messages, 50 memories, 48 tasks, 47 calendar events, 30 documents) to Supabase without data loss:

1. **Safety Guarantee:** The script will **never** modify or delete your local `backend/technopie.db`. It automatically saves a timestamped snapshot to `backend/backups/technopie_backup_<TIMESTAMP>.db`.
2. **Execute the Migration:**
   ```powershell
   python backend/scripts/migrate_sqlite_to_postgres.py --target-url "postgresql+asyncpg://postgres.[REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?ssl=require"
   ```
3. **Automated Parity Verification:**
   The migration engine extracts records in foreign-key topological order, converts ISO timestamps to UTC-aware datetimes, commits in atomic transactions, and performs a 100% row-count parity audit.

---

## 6. Supabase Tables Initialized

| Table | Purpose | Indexes / Constraints |
|---|---|---|
| `users` | Auth credentials, status, roles | `id` (PK, UUID), `email` (Unique, Index) |
| `user_profiles` | Preferences, language, tone, timezone | `id` (PK), `user_id` (FK, Unique, Cascade) |
| `conversations` | Executive sessions | `id` (PK), `user_id` (FK, Index, Cascade) |
| `messages` | Chat history, tool calls, token telemetry | `id` (PK), `conversation_id` (FK), `user_id` (FK) |
| `memories` | Semantic memory bank | `id` (PK), `user_id` (FK), `importance_score` |
| `tasks` | Deliverables, deadlines, statuses | `id` (PK), `user_id` (FK), `due_date`, `status` |
| `calendar_events` | Schedule, attendees, meeting links | `id` (PK), `user_id` (FK), `start_time`, `end_time` |
| `documents` | Generated executive briefs & metadata | `id` (PK), `user_id` (FK), `doc_type` |
| `connected_accounts` | Google OAuth tokens (encrypted) | `id` (PK), `user_id` (FK), `provider` |
| `automations` | Event triggers & background jobs | `id` (PK), `user_id` (FK) |
| `notifications` | System alerts & approval requests | `id` (PK), `user_id` (FK), `is_read` |
| `subscriptions` | Payment tiers & gateways | `id` (PK), `user_id` (FK, Unique) |
