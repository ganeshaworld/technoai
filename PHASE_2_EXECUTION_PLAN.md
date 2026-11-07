# TECHNOPIE AI — PHASE 2 EXECUTION PLAN
## Professional Assistance, Real AI Foundation & External Integrations

**Author:** Principal Software Architect, Principal AI Engineer, Backend Architect & SaaS Security Engineer  
**Organization:** Technopie Consultant Pvt. Ltd.  
**Product:** Technopie AI — "Your AI. Your Assistant. Your Productivity."  
**Date:** November 07, 2026  
**Status:** Approved for Implementation  

---

## 1. Executive Summary & Architecture Baseline

Phase 0 and Phase 1 established the core modular structure, relational database entities, executive UI, and simulated business logic. Phase 1.5 audited and eliminated critical security vulnerabilities (auth bypass, document IDOR, intent collision, and PRAGMA foreign keys).

Phase 2 transitions Technopie AI from an evaluated local prototype into a verified production-grade SaaS platform powered by:
1. **Real Foundation AI Inference:** Native Google Gemini integration with strict error propagation and removal of silent mock fallbacks.
2. **Persistent Enterprise Infrastructure:** Dual-engine PostgreSQL + pgvector persistence with versioned Alembic migrations.
3. **Verified Google Workspace Connectivity:** Official Google OAuth 2.0 with minimum read-only scopes, AES-256-GCM token encryption, and live Gmail/Calendar synchronization.
4. **Authentic Executive Workflows:** Multi-source daily briefings, email triage, and agenda analysis with zero synthetic or fabricated data.
5. **Rigorous Security Verification:** Tenant isolation verification, tool execution authorization, and cryptographic integrity.

---

## 2. Reusable Code & Existing Assets

The existing architecture provides high-leverage foundational assets that are preserved without destructive rewrites:

| Asset | Location | Reusability in Phase 2 |
|---|---|---|
| **Cognitive Brain Loop** | `backend/app/agents/orchestrator.py` | Preserved. The 6-stage cognitive loop (`UNDERSTAND -> REMEMBER -> PLAN -> EXECUTE -> VERIFY -> REPORT`) remains the orchestrator core. Tool outputs will feed directly into real Gemini system prompts. |
| **Model Abstraction** | `backend/app/services/ai_providers.py` | Preserved and hardened. `BaseLLMProvider` interface is retained; `GeminiProvider` is upgraded with retry policies, timeouts, and structured error handling. |
| **Relational Data Models** | `backend/app/db/models.py` | 100% reusable. `User`, `UserProfile`, `Conversation`, `Message`, `Task`, `Memory`, `CalendarEvent`, `Document`, `IntegrationToken`, and `AuditLog` are PostgreSQL-ready. |
| **Security & Guardrails** | `backend/app/core/security.py`, `guardrails.py` | Preserved. JWT validation, password hashing, and prompt-injection screening (`inspect_prompt_safety`) are active. |
| **Document Generation** | `backend/app/services/document_service.py` | 100% reusable. Native binary generation for DOCX, PDF, XLSX, PPTX is already functional and tested. |
| **Executive Frontend UI** | `frontend/src/` | 100% reusable. Next.js 14 App Router, Tailwind CSS, Lucide Icons, `ApprovalCard`, `VoiceButton`, and all 10 views are operational. |

---

## 3. Detailed File Modification Matrix

The following table itemizes the exact files undergoing modification or creation during Phase 2:

```mermaid
flowchart TD
    Config["backend/app/config.py"] --> Providers["backend/app/services/ai_providers.py"]
    Config --> DB["backend/app/db/session.py"]
    Config --> Crypto["backend/app/core/crypto.py"]
    Providers --> Orchestrator["backend/app/agents/orchestrator.py"]
    Orchestrator --> ChatRoutes["backend/app/api/chat_routes.py"]
    Crypto --> OAuth["backend/app/services/google_oauth.py"]
    OAuth --> Gmail["backend/app/services/email_service.py"]
    OAuth --> Calendar["backend/app/services/calendar_service.py"]
    DB --> Migrations["backend/alembic/"]
```

| Phase | Target File | Action | Technical Scope |
|---|---|---|---|
| **Phase 2A** | `backend/app/config.py` | Modify | Add `ALLOW_MOCK_FALLBACK`, provider timeout/retry thresholds, strict environment settings. |
| **Phase 2A** | `backend/app/services/ai_providers.py` | Refactor | Upgrade `GeminiProvider` with direct HTTP/SDK calls, 30s timeout, exponential backoff retries, usage logging, structured exceptions (`AIProviderError`, `AIProviderMissingKeyError`). Remove silent mock cascade. |
| **Phase 2A** | `backend/app/agents/orchestrator.py` | Modify | Handle provider exceptions gracefully; return explicit configuration errors when `GOOGLE_API_KEY` is absent. |
| **Phase 2A** | `backend/app/api/chat_routes.py` | Modify | Return accurate HTTP error codes (e.g., 503 for unconfigured provider, 429 for rate limit) instead of masking errors. |
| **Phase 2A** | `backend/tests/test_gemini_provider.py` | Create | Unit and integration test suite verifying timeouts, retries, error handling, and live API responses. |
| **Phase 2B** | `backend/app/db/session.py` | Modify | Support dual engine: dynamic fallback to SQLite in development, asynchronous `asyncpg` engine for PostgreSQL in production. |
| **Phase 2B** | `backend/alembic.ini`, `backend/alembic/` | Create | Configure Alembic versioned migrations with autogenerate support. |
| **Phase 2B** | `backend/scripts/migrate_sqlite_to_postgres.py` | Create | Safe zero-data-loss migration script from SQLite to PostgreSQL. |
| **Phase 2C** | `backend/app/core/crypto.py` | Create | AES-256-GCM token encryption and decryption engine using `cryptography.hazmat`. |
| **Phase 2C** | `backend/app/services/google_oauth.py` | Create | Google OAuth 2.0 PKCE flow, authorization URL generator, code-token exchange, token refresher, revocation. |
| **Phase 2C** | `backend/app/api/integration_routes.py` | Create | Endpoints: `GET /integrations/google/authorize`, `GET /integrations/google/callback`, `POST /integrations/google/disconnect`, `GET /integrations/google/status`. |
| **Phase 2C** | `backend/app/services/email_service.py` | Refactor | Real Gmail API client (`gmail.users.messages.list`, `get`) with read-only scope, thread categorization, draft preparation. |
| **Phase 2C** | `backend/app/services/calendar_service.py` | Refactor | Real Google Calendar API client (`events.list`) with read-only scope, conflict detection, daily briefing builder. |
| **Phase 2D** | `backend/app/agents/orchestrator.py` | Enhance | Implement real data attribution: workflows explicitly label sources (e.g., `[Gmail: 3 unread]`, `[Calendar: 2 events]`, `[Tasks: 4 pending]`). |
| **Phase 2E** | `backend/tests/test_security_regression.py` | Create | Test unauthenticated access, tenant isolation, expired token handling, prompt injection in emails. |

---

## 4. Required Environment Variables

All secrets must reside exclusively in environment variables and `.env`. No hardcoded credentials are permitted.

| Variable Name | Required By | Format / Example | Purpose |
|---|---|---|---|
| `GOOGLE_API_KEY` | Phase 2A | `AIzaSy...` | Foundation AI inference (Gemini 2.5 Flash / Pro). |
| `DEFAULT_AI_PROVIDER` | Phase 2A | `gemini` | Primary LLM provider (`gemini`, `openai`, `anthropic`, `mock`). |
| `ALLOW_MOCK_FALLBACK` | Phase 2A | `false` | When `false`, prohibits silent mock fallback if key is missing. |
| `DATABASE_URL` | Phase 2B | `postgresql+asyncpg://user:pass@host:5432/db` | Production PostgreSQL connection URL. |
| `GOOGLE_CLIENT_ID` | Phase 2C | `...apps.googleusercontent.com` | Google Cloud OAuth 2.0 Web Client ID. |
| `GOOGLE_CLIENT_SECRET` | Phase 2C | `GOCSPX-...` | Google Cloud OAuth 2.0 Web Client Secret. |
| `GOOGLE_REDIRECT_URI` | Phase 2C | `http://localhost:8000/api/integrations/google/callback` | OAuth redirect endpoint. |
| `TOKEN_ENCRYPTION_KEY` | Phase 2C | 32-byte Base64 or Hex key | Master encryption key for AES-256-GCM token storage. |
| `ENVIRONMENT` | All | `production` / `staging` / `development` | Deployment environment tier. |

---

## 5. Google Cloud Configuration Architecture

To enable Google Workspace integrations securely:

1. **GCP Project:** `technopie-ai-saas`
2. **APIs to Enable:**
   - Google Generative Language API (`generativelanguage.googleapis.com`)
   - Gmail API (`gmail.googleapis.com`)
   - Google Calendar API (`calendar-json.googleapis.com`)
3. **OAuth 2.0 Consent Screen:**
   - **User Type:** External (or Internal for Workspace organizations).
   - **Publishing Status:** Testing (add developer test emails) or In Production.
   - **Scopes (Strict Minimum Read-Only Principle):**
     - `https://www.googleapis.com/auth/gmail.readonly` (Inspect email threads & headers without write/delete permissions)
     - `https://www.googleapis.com/auth/calendar.readonly` (Inspect events & schedules without write/delete permissions)
     - `openid`, `https://www.googleapis.com/auth/userinfo.email`, `https://www.googleapis.com/auth/userinfo.profile`
4. **OAuth 2.0 Client Credentials (Web Application):**
   - **Authorized JavaScript Origins:** `http://localhost:3000`, `http://127.0.0.1:3000`
   - **Authorized Redirect URIs:** `http://localhost:8000/api/integrations/google/callback`, `http://127.0.0.1:8000/api/integrations/google/callback`

---

## 6. Database Migration Strategy & Risk Mitigation (Phase 2B)

Migrating from SQLite to PostgreSQL carries specific data integrity risks that require defensive architecture:

```mermaid
sequenceDiagram
    participant SQLite as SQLite Database (technopie.db)
    participant Script as Safe Migration Script
    participant Alembic as Alembic Migrations
    participant Postgres as PostgreSQL (Supabase / RDS)

    Note over SQLite,Postgres: Zero-Data-Loss Migration Workflow
    Script->>SQLite: 1. Full read-only backup & snapshot
    Alembic->>Postgres: 2. Apply latest schema migrations
    Script->>SQLite: 3. Extract all records (Users, Tasks, Memories, Docs, etc.)
    Script->>Postgres: 4. Insert records inside atomic transaction
    Postgres-->>Script: 5. Commit or Rollback on error
    Script->>Postgres: 6. Run verification parity checks (Row counts, FKs, Hashes)
    Note over SQLite: SQLite database is NEVER deleted
```

### Risk Analysis & Mitigations:

1. **Data Type Discrepancies:**
   - *Issue:* SQLite stores datetime as string; PostgreSQL requires `TIMESTAMP WITH TIME ZONE` (`timestamptz`).
   - *Mitigation:* Normalize all datetime fields to UTC ISO-8601 strings during extraction and parse into aware Python datetime objects before insertion.
2. **JSON Serialization:**
   - *Issue:* SQLite stores JSON columns as plain TEXT; PostgreSQL provides native `JSONB`.
   - *Mitigation:* Ensure models use SQLAlchemy's generic `JSON` type, which maps to `JSONB` on PostgreSQL and `TEXT` on SQLite seamlessly.
3. **Foreign Key Enforcement:**
   - *Issue:* PostgreSQL enforces foreign keys strictly on insertion order.
   - *Mitigation:* Migration script exports and imports in dependency order: `users` -> `user_profiles` -> `conversations` -> `messages` -> `tasks` -> `memories` -> `calendar_events` -> `documents` -> `integration_tokens` -> `audit_logs`.
4. **Rollback & Persistence Safeguards:**
   - The original `technopie.db` SQLite database file will **never** be deleted or modified during the migration. It remains the source of truth until PostgreSQL verification passes all parity checks.

---

## 7. Comprehensive Test Cases & Acceptance Criteria

### Phase 2A (Real AI Provider — Gemini):
- [ ] `TEST-2A-01`: Direct API inference returns valid completion using Gemini 2.5 Flash when `GOOGLE_API_KEY` is provided.
- [ ] `TEST-2A-02`: Missing `GOOGLE_API_KEY` raises structured `AIProviderMissingKeyError` (HTTP 503) and **never** returns mock output in production.
- [ ] `TEST-2A-03`: Transient network failures (HTTP 503, 429) trigger up to 3 exponential backoff retries.
- [ ] `TEST-2A-04`: Requests exceeding 30 seconds trigger timeout exception cleanly.
- [ ] `TEST-2A-05`: Token usage metadata (`totalTokenCount`) is logged accurately on every call.

### Phase 2B (PostgreSQL Migration):
- [ ] `TEST-2B-01`: Alembic runs schema migrations cleanly from scratch on fresh PostgreSQL database.
- [ ] `TEST-2B-02`: SQLite data export script imports 100% of rows without data loss.
- [ ] `TEST-2B-03`: Multi-user tenant isolation is verified across tasks, memories, documents, and messages.

### Phase 2C (Google OAuth & Integrations):
- [ ] `TEST-2C-01`: Google authorization URL contains only read-only scopes.
- [ ] `TEST-2C-02`: OAuth tokens are stored encrypted using AES-256-GCM; plain tokens never exist in database rows.
- [ ] `TEST-2C-03`: Disconnecting integration revokes token with Google API and purges local credentials.

### Phase 2D (Real Assistant Workflows):
- [ ] `TEST-2D-01`: Email triage lists real unread emails and explains urgency based on real body text.
- [ ] `TEST-2D-02`: Daily briefing merges real calendar events, active tasks, and unread emails with verified source attribution.
- [ ] `TEST-2D-03`: Outbound email drafts halt at Level 3 approval card and do not dispatch without manual confirmation.

### Phase 2E (Security & Hardening):
- [ ] `TEST-2E-01`: Unauthenticated API requests receive HTTP 401 across all endpoints.
- [ ] `TEST-2E-02`: Cross-tenant IDOR attacks on tasks, documents, and memories return HTTP 404/403.
- [ ] `TEST-2E-03`: Prompt injection attempts inside emails or documents are neutralized by guardrails.

---

## 8. API & Infrastructure Cost Estimates

| Component | Tier / Model | Unit Cost | Projected Monthly Cost (1,000 Active Users) |
|---|---|---|---|
| **AI Inference (Fast)** | Google Gemini 2.5 Flash | $0.075 / 1M Input Tokens<br/>$0.30 / 1M Output Tokens | ~$15.00 – $25.00 (Assuming 50k tokens/user/month) |
| **AI Inference (Complex)** | Google Gemini 2.5 Pro | $1.25 / 1M Input Tokens<br/>$5.00 / 1M Output Tokens | ~$25.00 – $40.00 (Assuming executive briefings & deep research) |
| **Database** | Managed PostgreSQL (Supabase Pro / RDS) | Compute + Storage | ~$25.00 / month |
| **Google Cloud APIs** | Gmail API & Google Calendar API | Free within standard quotas (250M units/day) | $0.00 |
| **Total Estimated Operating Cost** | | | **~$65.00 – $90.00 / month** |

---

## 9. Next Immediate Step: Phase 2A Execution

With this execution plan established, implementation initiates strictly with **Phase 2A (Real AI Provider — Google Gemini)**. Phase 2B will proceed only after Phase 2A passes all integration tests and acceptance gates.
