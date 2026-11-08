# Render Frontend Setup Guide: Next.js 14 SaaS Dashboard
## TECHNOPIE AI — Production Web Service Configuration

**Product:** Technopie AI Executive Dashboard  
**Hosting Platform:** Render Free Tier  
**Runtime:** Node 20.12.2  
**Framework:** Next.js 14 (App Router)  

---

## 1. Web Service Parameters

When creating the frontend Web Service in the [Render Dashboard](https://dashboard.render.com), configure the following settings:

| Field | Configuration Value | Critical Notes |
|---|---|---|
| **Name** | `technopie-ai-frontend` | Subdomain generated on Render |
| **Region** | Same region as backend | Reduces cross-service network latency |
| **Branch** | `main` | Production branch |
| **Root Directory** | `frontend` | **Set to `frontend`** so npm commands execute inside Next.js folder |
| **Runtime** | `Node` | Node.js environment |
| **Build Command** | `npm install && npm run build` | Builds optimized production static & server bundles |
| **Start Command** | `npm run start` | Executes `next start` on Render's dynamic `$PORT` |
| **Auto-Deploy** | `Yes` | Automatically redeploys on git push |
| **Plan Type** | `Free` | 512 MB RAM, 0.1 CPU |

---

## 2. Environment Variables Configuration

In Render Dashboard → **`technopie-ai-frontend`** → **Environment**, add the following key-value pairs:

```env
# Backend API Base URL (Must point to your Render backend web service with /api suffix)
NEXT_PUBLIC_API_URL=https://technopie-ai-backend.onrender.com/api

# Node.js LTS Runtime Version Pin
NODE_VERSION=20.12.2
```

> ⚠️ **Important Build-Time Context:**
> In Next.js, all environment variables prefixed with `NEXT_PUBLIC_` are inlined into the client-side JavaScript bundles **at build time**.
> If you change `NEXT_PUBLIC_API_URL`, you must trigger a **Manual Deploy → Clear build cache & deploy** in Render for the updated URL to take effect in the browser.

---

## 3. Production Build Validation

To verify that the frontend builds without errors before pushing to GitHub:

```powershell
# From local repository root:
npm run build --prefix frontend
```

Expected Output:
```
  ▲ Next.js 14.2.35
   Creating an optimized production build ...
 ✓ Compiled successfully
   Linting and checking validity of types ...
   Collecting page data ...
 ✓ Generating static pages (4/4)
   Finalizing page optimization ...
Route (app)                              Size     First Load JS
┌ ○ /                                    21.6 kB         109 kB
└ ○ /_not-found                          873 B          88.2 kB
```

---

## 4. Post-Deploy Interconnection Check

Once Render finishes deploying both services:
1. Open `https://technopie-ai-frontend.onrender.com` in your browser.
2. Open Browser DevTools (**F12** → **Network** tab).
3. The dashboard executes an automatic session initialization calling `POST /api/auth/login`.
4. Verify:
   - Status code: `200 OK`
   - Response headers include `access-control-allow-origin: https://technopie-ai-frontend.onrender.com`
   - Dashboard initializes and displays "Alexander Vance" with Executive Assistant welcome prompt.

---

## 5. Troubleshooting Common Frontend Issues

### Issue 1: `NetworkError when attempting to fetch resource`
- **Cause:** CORS mismatch or backend is sleeping.
- **Fix:** Verify backend `CORS_ORIGINS` contains `https://technopie-ai-frontend.onrender.com`. If backend was asleep, wait 30 seconds for cold start.

### Issue 2: `NEXT_PUBLIC_API_URL pointing to localhost:8000`
- **Cause:** `NEXT_PUBLIC_API_URL` was not configured before the build ran.
- **Fix:** In Render Dashboard → Environment, verify `NEXT_PUBLIC_API_URL`, then click **Manual Deploy → Clear build cache & deploy**.
