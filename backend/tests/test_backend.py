import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.db.session import init_db

async def get_auth_token(email="test_exec@technopie.ai", password="Password123!"):
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        await ac.post("/api/auth/register", json={
            "email": email,
            "password": password,
            "full_name": "Alexander Vance",
            "profession": "CEO"
        })
        login_res = await ac.post("/api/auth/login", json={"email": email, "password": password})
        return login_res.json()["access_token"]

@pytest.mark.asyncio
async def test_health_endpoint():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Technopie AI" in data["platform"]

@pytest.mark.asyncio
async def test_unauthenticated_request_blocked():
    """Verify SEC-01 fix: Unauthenticated requests MUST return 401 Unauthorized."""
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r_tasks = await ac.get("/api/tasks")
        assert r_tasks.status_code == 401
        r_memories = await ac.get("/api/memories")
        assert r_memories.status_code == 401

@pytest.mark.asyncio
async def test_auth_registration_and_login():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        reg_payload = {
            "email": "fresh_exec_test@technopie.ai",
            "password": "Password123!",
            "full_name": "Alexander Vance",
            "profession": "CEO"
        }
        res = await ac.post("/api/auth/register", json=reg_payload)
        assert res.status_code in (200, 400)

        login_res = await ac.post("/api/auth/login", json={
            "email": "fresh_exec_test@technopie.ai",
            "password": "Password123!"
        })
        assert login_res.status_code == 200
        token_data = login_res.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_task_crud():
    token = await get_auth_token("task_user@technopie.ai")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers={"Authorization": f"Bearer {token}"}) as ac:
        # Get tasks
        get_res = await ac.get("/api/tasks")
        assert get_res.status_code == 200
        tasks = get_res.json()
        assert isinstance(tasks, list)

        # Create task
        create_res = await ac.post("/api/tasks", json={
            "title": "Review Q4 SaaS expansion roadmap",
            "priority": "high",
            "tags": ["Strategy", "Executive"]
        })
        assert create_res.status_code == 200
        task_data = create_res.json()
        assert task_data["title"] == "Review Q4 SaaS expansion roadmap"
        task_id = task_data["id"]

        # Update task
        patch_res = await ac.patch(f"/api/tasks/{task_id}", json={
            "status": "completed"
        })
        assert patch_res.status_code == 200

@pytest.mark.asyncio
async def test_memory_crud():
    token = await get_auth_token("memory_user@technopie.ai")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers={"Authorization": f"Bearer {token}"}) as ac:
        # List memories
        mem_res = await ac.get("/api/memories")
        assert mem_res.status_code == 200
        memories = mem_res.json()
        assert len(memories) > 0

        # Add memory
        add_res = await ac.post("/api/memories", json={
            "category": "preference",
            "content": "Prefers asynchronous communication before noon.",
            "importance_score": 1.0
        })
        assert add_res.status_code == 200
        mem_id = add_res.json()["id"]

        # Delete memory
        del_res = await ac.delete(f"/api/memories/{mem_id}")
        assert del_res.status_code == 200

@pytest.mark.asyncio
async def test_ai_brain_scenarios():
    """Verify AI-01 and AI-02 fixes: Natural language memory and task creation."""
    token = await get_auth_token("ai_user@technopie.ai")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers={"Authorization": f"Bearer {token}"}) as ac:
        # 1. Store memory
        r_store = await ac.post("/api/chat/message", json={
            "message": "Remember that my preferred language is English."
        })
        assert r_store.status_code == 200
        assert "Preference Stored" in r_store.json()["content"]

        # 2. Recall memory
        r_recall = await ac.post("/api/chat/message", json={
            "message": "What is my preferred language?"
        })
        assert r_recall.status_code == 200
        assert "English" in r_recall.json()["content"]

        # 3. Create task with temporal parameter
        r_task = await ac.post("/api/chat/message", json={
            "message": "Create a task to prepare a business proposal tomorrow."
        })
        assert r_task.status_code == 200
        assert "Task Created Successfully" in r_task.json()["content"]

@pytest.mark.asyncio
async def test_document_generation_and_idor_prevention():
    """Verify SEC-02 fix: Document download requires auth & ownership."""
    token_a = await get_auth_token("doc_user_a@technopie.ai")
    token_b = await get_auth_token("doc_user_b@technopie.ai")
    transport = ASGITransport(app=app)

    # User A generates DOCX
    async with AsyncClient(transport=transport, base_url="http://test", headers={"Authorization": f"Bearer {token_a}"}) as ac_a:
        doc_res = await ac_a.post("/api/documents/generate", json={
            "title": "Automated Executive Brief",
            "doc_type": "docx",
            "content": "## Automated Test Brief\n- Test item 1\n- Test item 2"
        })
        assert doc_res.status_code == 200
        doc_id = doc_res.json()["id"]

        # User A can download their own document
        dl_a = await ac_a.get(f"/api/documents/{doc_id}/download")
        assert dl_a.status_code == 200
        assert len(dl_a.content) > 0

    # User B cannot download User A's document
    async with AsyncClient(transport=transport, base_url="http://test", headers={"Authorization": f"Bearer {token_b}"}) as ac_b:
        dl_b = await ac_b.get(f"/api/documents/{doc_id}/download")
        assert dl_b.status_code in (403, 404)
