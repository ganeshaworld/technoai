# Master Environment Variables Reference
## TECHNOPIE AI — Cloud Configuration & Security Standards

**Version:** 2.0  
**Updated:** November 08, 2026  
**Security Standard:** Zero Hardcoded Secrets — 100% Environment Injection  

---

## 1. Backend Web Service (`technopie-ai-backend` on Render)

| Variable Name | Required | Default / Format | Description & Production Value |
|---|---|---|---|
| `ENVIRONMENT` | **YES** | `development` | Deployment environment tier. Set to `production` on Render. |
| `DEBUG` | **YES** | `True` | Debug mode toggle. Set to `False` in production to prevent stack trace leaks. |
| `APP_NAME` | No | `Technopie AI` | SaaS Platform display name. |
| `APP_URL` | No | `http://localhost:3000` | Frontend dashboard public URL (e.g. `https://technopie-ai-frontend.onrender.com`). |
| `API_BASE_URL` | No | `http://localhost:8000/api` | Backend API base path. |
| `SECRET_KEY` | **YES** | 64-character hex | Cryptographic secret used for signing and verifying JWT tokens. Generate via `openssl rand -hex 32`. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `1440` (24h) | JWT access token lifetime in minutes. |
| `DATABASE_URL` | **YES** | `sqlite+aiosqlite:///...` | Async PostgreSQL connection string. Must use **Supabase IPv4 Pooler** URL on port `6543`: `postgresql+asyncpg://postgres.[REF]:[PASS]@aws-0-[REGION].pooler.supabase.com:6543/postgres?ssl=require`. |
| `DEFAULT_AI_PROVIDER` | **YES** | `gemini` | Foundation LLM Provider (`gemini`, `openai`, `anthropic`, `mock`). |
| `DEFAULT_FAST_MODEL` | No | `gemini-2.5-flash` | Fast execution model for routine triage and summaries. |
| `DEFAULT_REASONING_MODEL` | No | `gemini-2.5-pro` | Deep reasoning model for multi-step executive briefings. |
| `ALLOW_MOCK_FALLBACK` | **YES** | `false` | When `false`, prohibits silent mock cascade in production. |
| `GOOGLE_API_KEY` | **YES** | `AIzaSy...` | Foundation AI inference API key from [Google AI Studio](https://aistudio.google.com/). |
| `CORS_ORIGINS` | **YES** | `http://localhost:3000` | Comma-separated list of authorized browser origins. Set to: `https://technopie-ai-frontend.onrender.com,http://localhost:3000`. |
| `AI_REQUEST_TIMEOUT_SECONDS`| No | `30.0` | Upstream API timeout threshold. |
| `AI_MAX_RETRIES` | No | `3` | Maximum retry attempts on transient network errors / HTTP 429. |
| `AI_RETRY_BACKOFF_FACTOR` | No | `1.5` | Exponential backoff multiplier between retry attempts. |
| `GOOGLE_CLIENT_ID` | Optional | `...apps.googleusercontent.com` | Google Cloud OAuth 2.0 Web Client ID (for Gmail & Calendar). |
| `GOOGLE_CLIENT_SECRET` | Optional | `GOCSPX-...` | Google Cloud OAuth 2.0 Web Client Secret. |
| `GOOGLE_REDIRECT_URI` | Optional | `http://localhost:8000/...` | Authorized OAuth 2.0 redirect callback URL: `https://technopie-ai-backend.onrender.com/api/integrations/google/callback`. |
| `TOKEN_ENCRYPTION_KEY` | Optional | 32-byte string | AES-256-GCM master key used to encrypt OAuth refresh tokens at rest. |
| `PYTHON_VERSION` | **YES** | `3.11.9` | Render Python runtime version pin. |

---

## 2. Frontend Web Service (`technopie-ai-frontend` on Render / Vercel)

| Variable Name | Required | Default / Format | Description & Production Value |
|---|---|---|---|
| `NEXT_PUBLIC_API_URL` | **YES** | `http://localhost:8000/api` | Public base URL used by browser fetch requests. Set to `https://technopie-ai-backend.onrender.com/api`. Must include the `/api` suffix. |
| `NODE_VERSION` | **YES** | `20.12.2` | Render Node.js runtime version pin. |

> ⚠️ **Next.js Build-Time Notice:**
> In Next.js, `NEXT_PUBLIC_*` variables are embedded into JavaScript bundles during `npm run build`. If you change `NEXT_PUBLIC_API_URL` on Render, trigger a **Manual Deploy → Clear build cache & deploy** to update the client bundles.

---

## 3. Database Credentials (Supabase)

| Variable Name | Purpose | Example Value |
|---|---|---|
| `SUPABASE_URL` | Supabase Project API Gateway | `https://abcdefghijklmnop.supabase.co` |
| `SUPABASE_ANON_KEY` | Public Anon API Key | `eyJhbGciOi...` |
| `SUPABASE_SERVICE_ROLE_KEY` | Elevated Service Role Key (Backend Only) | `eyJhbGciOi...` |
