# API Documentation & Contracts
## TECHNOPIE AI — REST & SSE API Reference

**Base URL:** `http://localhost:8000/api` (Development) / `https://api.technopie.ai/api` (Production)  
**Standard Authentication:** `Authorization: Bearer <JWT_ACCESS_TOKEN>`  
**Content-Type:** `application/json` (except SSE streams: `text/event-stream` and file uploads: `multipart/form-data`)

---

## 1. System & Health

### `GET /health`
Returns system status, active providers, and database connectivity.
- **Response `200 OK`**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "active_providers": ["openai", "gemini", "anthropic", "mock"],
  "database": "connected"
}
```

---

## 2. Authentication & Profile

### `POST /auth/register`
Create a new user account.
- **Request Body:**
```json
{
  "email": "executive@technopie.com",
  "password": "StrongPassword123!",
  "full_name": "Alexander Vance"
}
```

### `POST /auth/login`
Authenticate user and obtain JWT tokens.
- **Response `200 OK`:**
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "c1f7b7a2-...",
    "email": "executive@technopie.com",
    "full_name": "Alexander Vance",
    "onboarding_completed": false
  }
}
```

### `GET /profile`
Fetch current user profile and executive preferences.

### `PUT /profile/onboarding`
Complete the guided executive onboarding questionnaire.
- **Request Body:**
```json
{
  "profession": "Chief Executive Officer",
  "work_description": "Managing enterprise technology strategy and investor relations",
  "preferred_language": "en",
  "timezone": "Asia/Kolkata",
  "productivity_goals": ["Zero inbox by end of day", "Automated morning briefings", "Daily task prioritization"],
  "ai_tone_preference": "executive"
}
```

---

## 3. AI Assistant & Conversations

### `GET /conversations`
List active user conversations.

### `POST /conversations`
Create a new conversation session.
- **Request Body:**
```json
{
  "title": "Strategy Session",
  "agent_type": "general_assistant"
}
```

### `POST /chat/stream`
Send a natural-language prompt and receive a real-time Server-Sent Events (SSE) token stream.
- **Request Body:**
```json
{
  "conversation_id": "c1f7b7a2-...",
  "message": "Prepare my schedule for tomorrow, check important emails and identify unfinished tasks.",
  "provider": "gemini", 
  "model": "gemini-2.5-flash"
}
```
- **SSE Stream Events:**
  - `event: thinking` $\rightarrow$ JSON payload with internal cognitive step (Understand, Remember, Plan)
  - `event: tool_call` $\rightarrow$ JSON payload indicating agent tool invocation (e.g. `calendar.get_events`, `task.list`)
  - `event: token` $\rightarrow$ Text chunk for real-time markdown streaming
  - `event: action_required` $\rightarrow$ Level 3 authorization card (e.g. Confirm email draft dispatch)
  - `event: done` $\rightarrow$ Full finalized message record with metadata and token counters

---

## 4. Personal Memory Management

### `GET /memories`
List all long-term memories with category filters (`personal`, `professional`, `preference`, `habit`, `goal`).

### `POST /memories`
Explicitly add a new memory item.
- **Request Body:**
```json
{
  "category": "preference",
  "content": "Prefers meetings scheduled between 10:00 AM and 1:00 PM; no Friday afternoon calls.",
  "importance_score": 1.0
}
```

### `PUT /memories/{id}`
Update an existing memory item.

### `DELETE /memories/{id}`
Permanently delete an individual memory entity.

### `DELETE /memories/clear-all`
Clear all saved user memories.

---

## 5. Executive Task Management

### `GET /tasks`
Fetch tasks with optional filters: `status` (todo, in_progress, completed), `priority` (low, medium, high, urgent), `view` (today, upcoming, overdue, all).

### `POST /tasks`
Create a task manually or programmatically.
- **Request Body:**
```json
{
  "title": "Review Q3 Financial Deck with CFO",
  "description": "Examine burn rate projections and vendor budget adjustments.",
  "priority": "high",
  "due_date": "2026-11-08T15:00:00Z",
  "tags": ["Finance", "Strategy"]
}
```

### `PATCH /tasks/{id}`
Update task details or toggle status.

### `DELETE /tasks/{id}`
Remove a task.

---

## 6. Calendar & Email

### `GET /calendar/events`
Fetch upcoming meetings and calendar events.

### `POST /calendar/events`
Schedule a new meeting (with conflict detection).

### `GET /calendar/briefing`
Generate an AI-powered morning schedule briefing and conflict analysis.

### `GET /emails/inbox`
Fetch categorized emails (*Action Required*, *VIP*, *Newsletters*).

### `POST /emails/draft-reply`
Generate an AI draft reply matching the user's executive tone.

### `POST /emails/send`
Execute email dispatch (Requires Level 3 authorization confirmation).

---

## 7. Multi-Format Document Generation

### `POST /documents/generate`
Generate an executive document (`docx`, `pdf`, `xlsx`, `pptx`, `csv`).
- **Request Body:**
```json
{
  "title": "Executive AI Strategy Proposal",
  "doc_type": "docx",
  "prompt": "Create a 3-page comprehensive AI adoption roadmap for enterprise logistics.",
  "metadata": {"confidential": true, "author": "Technopie Consultant"}
}
```
- **Response `201 Created`:**
```json
{
  "id": "d820...",
  "title": "Executive AI Strategy Proposal",
  "doc_type": "docx",
  "file_size_bytes": 48320,
  "download_url": "/api/documents/d820.../download",
  "status": "ready"
}
```

### `GET /documents/{id}/download`
Securely download the generated file binary.

---

## 8. Deep Research Assistant

### `POST /research/query`
Trigger multi-source web research and fact synthesis.
- **Request Body:**
```json
{
  "query": "Autonomous AI agent market trends 2026 enterprise adoption",
  "depth": "comprehensive"
}
```
- **Response `200 OK`:** Returns structured report with verified facts, estimates, sources, and executive summary.

---

## 9. Automations & Connected Apps

### `GET /automations`
List active automations and execution history.

### `POST /automations`
Create a new triggered automation rule.

### `GET /integrations`
List status of connected accounts (Google Workspace, Microsoft 365, Slack).

### `POST /integrations/{provider}/connect`
Initiate OAuth 2.0 authorization URL.

---

## 10. Voice Assistant

### `POST /voice/transcribe`
Convert user audio recording to text (Whisper / Speech-to-Text).

### `POST /voice/synthesize`
Convert assistant response to audio speech stream (Text-to-Speech).

---

## 11. Subscription & Billing

### `GET /billing/plans`
Fetch plan definitions (*Free*, *Personal*, *Professional*, *Executive*, *Business*).

### `POST /billing/create-checkout-session`
Initiate Razorpay or Stripe payment flow.

---

## 12. Admin Console

### `GET /admin/stats`
Platform metrics: active users, token consumption by provider, API expenses, error rates.
