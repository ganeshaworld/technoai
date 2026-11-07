# Bugs, Defects & Remediation Log
## TECHNOPIE AI — Defect Tracking & Resolution Specifications

**Audit Date:** November 07, 2026  
**Standards:** Problem ➔ Root Cause ➔ Impact ➔ Recommended Fix ➔ Verification Method  

---

### DEFECT SEC-01: Authentication Bypass via Default Demo User Fallback
- **Severity:** **CRITICAL**
- **Affected File:** [`backend/app/core/security.py`](file:///d:/AntiGravity/technoai/backend/app/core/security.py)
- **Problem:** Requests to protected endpoints without an `Authorization` header succeed with HTTP 200 instead of failing with HTTP 401.
- **Root Cause:** `get_current_user_optional()` returned the `demo@technopie.ai` user whenever the token was absent. `get_current_user()` delegates to `get_current_user_optional()` and only checks `if not user`. Because a user was always returned, the authentication requirement was rendered ineffective.
- **Impact:** Complete exposure and unauthorized manipulation of demo tenant data across tasks, memories, and calendars by anonymous Internet clients.
- **Recommended Fix:** Enforce strict token requirement:
  ```python
  async def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
      if not token:
          raise HTTPException(status_code=401, detail="Authentication required")
      payload = decode_access_token(token)
      if not payload or "sub" not in payload:
          raise HTTPException(status_code=401, detail="Invalid token")
      ...
  ```
- **Verification Method:** Send `GET /api/tasks` with no headers and verify response is HTTP 401 Unauthorized.

---

### DEFECT SEC-02: Broken Object Level Authorization (IDOR) on Document Download
- **Severity:** **HIGH**
- **Affected File:** [`backend/app/api/document_routes.py`](file:///d:/AntiGravity/technoai/backend/app/api/document_routes.py)
- **Problem:** `GET /documents/{document_id}/download` allows downloading any document without verifying user ownership or authentication.
- **Root Cause:** Route handler lacked `user: User = Depends(get_current_user)` and did not filter by `Document.user_id == user.id`.
- **Impact:** Any user or unauthenticated caller knowing a document UUID can download confidential documents belonging to another tenant.
- **Recommended Fix:** Add authentication dependency and enforce `where(Document.id == document_id, Document.user_id == user.id)`.
- **Verification Method:** Have User B attempt to download User A's document and verify response is HTTP 404/403.

---

### DEFECT AI-01: Natural Language Memory Extraction Not Implemented
- **Severity:** **HIGH**
- **Affected File:** [`backend/app/agents/orchestrator.py`](file:///d:/AntiGravity/technoai/backend/app/agents/orchestrator.py)
- **Problem:** Commands such as *"Remember that my preferred language is English"* are not parsed or saved to the `memories` table. Subsequent queries cannot recall the stored fact.
- **Root Cause:** `CentralAIBrain._classify_intent()` categorized the prompt as `"general_executive_query"`. No logic existed to detect memory-storing intent or call `MemoryService.add_memory()`.
- **Impact:** The assistant fails core executive assistant workflow requirement (Stage 2: REMEMBER).
- **Recommended Fix:** Add regex/intent matching for `remember that...` and `my preference is...`, extract the content, and call `MemoryService.add_memory(db, user_id=user.id, category="preference", content=fact)`.
- **Verification Method:** Execute Scenario 1 and verify memory row count increments and Scenario 2 recalls the stored language.

---

### DEFECT AI-02: Keyword Collision Overrides Task Creation with Schedule Briefing
- **Severity:** **HIGH**
- **Affected File:** [`backend/app/agents/orchestrator.py`](file:///d:/AntiGravity/technoai/backend/app/agents/orchestrator.py)
- **Problem:** Prompt *"Create a task to prepare a business proposal tomorrow"* triggers a daily schedule briefing and creates 0 tasks.
- **Root Cause:** In `_classify_intent()`, the check for `"tomorrow"` occurred under `"schedule_and_day"` before `"task_management"`.
- **Impact:** Users attempting to create scheduled tasks have their instructions ignored.
- **Recommended Fix:** Prioritize explicit task creation commands (`create a task`, `add task`, `remind me to`) ahead of temporal schedule keywords.
- **Verification Method:** Execute Scenario 3 and verify that a task titled *"prepare a business proposal"* is created with tomorrow's due date.

---

### DEFECT AI-03: Analytical Task Requests Erroneously Insert Tasks
- **Severity:** **HIGH**
- **Affected File:** [`backend/app/agents/orchestrator.py`](file:///d:/AntiGravity/technoai/backend/app/agents/orchestrator.py)
- **Problem:** Prompt *"Analyze my pending tasks and prioritize them"* inserts a task into the database titled *"Analyze my pending tasks and prioritize them"*.
- **Root Cause:** Any prompt containing `"task"` was routed to task creation rather than task analysis.
- **Impact:** Analytical queries pollute the user's task board.
- **Recommended Fix:** Distinguish between task creation verbs (`create`, `add`, `remind`) and analytical verbs (`analyze`, `review`, `prioritize`, `list`). For analytical queries, list tasks without inserting new records.
- **Verification Method:** Execute Scenario 4 and verify that task count does not increase.

---

### DEFECT SEC-03: Dead Code in Prompt Injection Defense
- **Severity:** **MEDIUM**
- **Affected File:** [`backend/app/agents/orchestrator.py`](file:///d:/AntiGravity/technoai/backend/app/agents/orchestrator.py)
- **Problem:** `inspect_prompt_safety()` was defined in `guardrails.py` but never called in `orchestrator.py`.
- **Root Cause:** Omission during orchestrator wiring.
- **Impact:** Jailbreak attempts and prompt injection strings are passed directly to the model.
- **Recommended Fix:** Call `inspect_prompt_safety(prompt)` at the start of `CentralAIBrain.process_executive_request()`.
- **Verification Method:** Send a jailbreak string and verify that the system flags/sanitizes the prompt.

---

### DEFECT INT-01: Inaccurate Integration Status in Admin API
- **Severity:** **LOW**
- **Affected File:** [`backend/app/api/admin_routes.py`](file:///d:/AntiGravity/technoai/backend/app/api/admin_routes.py)
- **Problem:** Google Workspace is hardcoded as `status: "connected"` in the integrations API.
- **Root Cause:** Static mock response violating Requirement 18 ("Never display a connected status unless the connection has actually succeeded").
- **Impact:** False representation of integration readiness.
- **Recommended Fix:** Change status to `"available"` and only mark as `"connected"` if an active row exists in `connected_accounts`.
- **Verification Method:** Query `/api/integrations` and verify status is `"available"`.
