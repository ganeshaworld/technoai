import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.db.session import init_db

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
async def test_auth_registration_and_login():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Register new user
        reg_payload = {
            "email": "test_exec@technopie.ai",
            "password": "Password123!",
            "full_name": "Alexander Vance",
            "profession": "CEO"
        }
        res = await ac.post("/api/auth/register", json=reg_payload)
        assert res.status_code in (200, 400) # 200 on first run, 400 if already registered

        # Login
        login_res = await ac.post("/api/auth/login", json={
            "email": "test_exec@technopie.ai",
            "password": "Password123!"
        })
        assert login_res.status_code == 200
        token_data = login_res.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_task_crud():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
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
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
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
async def test_ai_brain_chat():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Send prompt to AI Assistant
        chat_res = await ac.post("/api/chat/message", json={
            "message": "Prepare my schedule for tomorrow, check important emails and identify unfinished tasks."
        })
        assert chat_res.status_code == 200
        data = chat_res.json()
        assert "content" in data
        assert "plan_steps" in data
        assert len(data["plan_steps"]) > 0

@pytest.mark.asyncio
async def test_document_generation():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Generate DOCX
        doc_res = await ac.post("/api/documents/generate", json={
            "title": "Automated Executive Brief",
            "doc_type": "docx",
            "content": "## Automated Test Brief\n- Test item 1\n- Test item 2"
        })
        assert doc_res.status_code == 200
        doc_data = doc_res.json()
        doc_id = doc_data["id"]

        # Download doc
        download_res = await ac.get(f"/api/documents/{doc_id}/download")
        assert download_res.status_code == 200
        assert len(download_res.content) > 0
