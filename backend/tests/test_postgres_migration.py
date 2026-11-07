import os
import sys
import uuid
import pytest
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select, func
from backend.app.config import settings
from backend.app.db.session import (
    get_normalized_database_url,
    AsyncSessionLocal,
    engine,
    Base
)
from backend.app.db.models import (
    User, UserProfile, Conversation, Message,
    Memory, Task, CalendarEvent, Document
)
from backend.app.core.security import hash_password
from backend.scripts.migrate_sqlite_to_postgres import (
    create_sqlite_immutable_backup,
    run_migration,
    MODEL_HIERARCHY
)

# ------------------------------------------------------------------------------
# 1. Database URL Normalization Tests
# ------------------------------------------------------------------------------

def test_database_url_normalization():
    """Verify standard PostgreSQL URLs are normalized to asyncpg dialect."""
    raw_supabase = "postgres://postgres:secret@db.project.supabase.co:5432/postgres"
    assert get_normalized_database_url(raw_supabase) == "postgresql+asyncpg://postgres:secret@db.project.supabase.co:5432/postgres"

    raw_rds = "postgresql://admin:password@rds.amazonaws.com:5432/technopie"
    assert get_normalized_database_url(raw_rds) == "postgresql+asyncpg://admin:password@rds.amazonaws.com:5432/technopie"

    sqlite_url = "sqlite+aiosqlite:///backend/technopie.db"
    assert get_normalized_database_url(sqlite_url) == sqlite_url


# ------------------------------------------------------------------------------
# 2. Immutable Backup Verification
# ------------------------------------------------------------------------------

def test_sqlite_immutable_backup_created():
    """Verify backup file is created in backend/backups and matches source size."""
    sqlite_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../technopie.db"))
    if not os.path.exists(sqlite_file):
        pytest.skip("technopie.db not present in local test directory")

    backup_path = create_sqlite_immutable_backup(sqlite_file)
    assert os.path.exists(backup_path)
    assert os.path.getsize(backup_path) == os.path.getsize(sqlite_file)
    assert "technopie_backup_" in os.path.basename(backup_path)


# ------------------------------------------------------------------------------
# 3. Safe Migration & Parity Verification on Target Engine
# ------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_migration_and_parity_verification(tmp_path):
    """Test full migration pipeline to an isolated target engine and verify parity."""
    target_db_file = tmp_path / "test_target.db"
    target_url = f"sqlite+aiosqlite:///{target_db_file}"

    sqlite_source = settings.DATABASE_URL

    res = await run_migration(source_url=sqlite_source, target_url=target_url, dry_run=False)

    assert res["status"] == "success"
    assert res["parity_verified"] is True
    assert res["source_sqlite_preserved"] is True

    # Audit row counts directly on target
    target_engine = create_async_engine(target_url, echo=False)
    target_session = async_sessionmaker(target_engine, expire_on_commit=False, class_=AsyncSession)

    async with target_session() as session:
        for table_name, model_cls in MODEL_HIERARCHY:
            stmt = select(func.count()).select_from(model_cls)
            target_count = (await session.execute(stmt)).scalar()
            expected_count = res["records_migrated"][table_name]
            assert target_count == expected_count, f"Parity mismatch for table {table_name}"

    await target_engine.dispose()


# ------------------------------------------------------------------------------
# 4. Persistence After Engine Restart
# ------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_persistence_after_engine_restart():
    """Verify data survives connection tear-down and engine disposal."""
    test_user_id = str(uuid.uuid4())
    test_email = f"restart_test_{uuid.uuid4().hex[:8]}@technopie.ai"

    # Step 1: Write entities
    async with AsyncSessionLocal() as db:
        user = User(
            id=test_user_id,
            email=test_email,
            hashed_password=hash_password("RestartPass123!")
        )
        task = Task(
            user_id=test_user_id,
            title="Strategic Persistence Review",
            priority="high",
            status="todo"
        )
        memory = Memory(
            user_id=test_user_id,
            category="preference",
            content="Persistent executive preference"
        )
        conv = Conversation(
            user_id=test_user_id,
            title="Persisted Executive Briefing",
            agent_type="general_assistant"
        )
        db.add_all([user, task, memory, conv])
        await db.commit()

    # Step 2: Simulate server reboot / connection pool disposal
    await engine.dispose()

    # Step 3: Re-query from a fresh connection session
    async with AsyncSessionLocal() as db:
        # Check User
        stmt_user = select(User).where(User.id == test_user_id)
        u = (await db.execute(stmt_user)).scalars().first()
        assert u is not None
        assert u.email == test_email

        # Check Task
        stmt_task = select(Task).where(Task.user_id == test_user_id)
        t = (await db.execute(stmt_task)).scalars().first()
        assert t is not None
        assert t.title == "Strategic Persistence Review"

        # Check Memory
        stmt_mem = select(Memory).where(Memory.user_id == test_user_id)
        m = (await db.execute(stmt_mem)).scalars().first()
        assert m is not None
        assert m.content == "Persistent executive preference"

        # Check Conversation
        stmt_conv = select(Conversation).where(Conversation.user_id == test_user_id)
        c = (await db.execute(stmt_conv)).scalars().first()
        assert c is not None
        assert c.title == "Persisted Executive Briefing"


# ------------------------------------------------------------------------------
# 5. Strict Tenant Data Isolation Across All User Entities
# ------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_tenant_data_isolation():
    """
    Verify strict tenant data isolation between two users:
    User Alpha's data must be completely inaccessible to User Beta.
    """
    alpha_id = str(uuid.uuid4())
    beta_id = str(uuid.uuid4())
    alpha_email = f"alpha_{uuid.uuid4().hex[:8]}@technopie.ai"
    beta_email = f"beta_{uuid.uuid4().hex[:8]}@technopie.ai"

    async with AsyncSessionLocal() as db:
        # Create User Alpha & User Beta
        user_alpha = User(id=alpha_id, email=alpha_email, hashed_password=hash_password("PassAlpha123!"))
        user_beta = User(id=beta_id, email=beta_email, hashed_password=hash_password("PassBeta123!"))
        db.add_all([user_alpha, user_beta])
        await db.flush()

        # User Alpha creates resources across all domains
        task_alpha = Task(user_id=alpha_id, title="Alpha Private Acquisition Task", priority="urgent")
        mem_alpha = Memory(user_id=alpha_id, category="preference", content="Alpha secret habit")
        doc_alpha = Document(user_id=alpha_id, title="Alpha Q3 Financial Model", doc_type="xlsx", file_path="uploads/alpha_model.xlsx")
        conv_alpha = Conversation(user_id=alpha_id, title="Alpha Confidential Meeting")
        db.add_all([task_alpha, mem_alpha, doc_alpha, conv_alpha])
        await db.flush()

        msg_alpha = Message(
            conversation_id=conv_alpha.id,
            user_id=alpha_id,
            sender_role="user",
            content="Alpha private communication"
        )
        cal_alpha = CalendarEvent(
            user_id=alpha_id,
            title="Alpha Board Strategy",
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc)
        )
        db.add_all([msg_alpha, cal_alpha])
        await db.commit()

    # Verify Isolation: User Beta queries all tables filtered by User Beta's tenant ID
    async with AsyncSessionLocal() as db:
        # 1. Tasks Isolation
        tasks_beta = (await db.execute(select(Task).where(Task.user_id == beta_id))).scalars().all()
        assert len(tasks_beta) == 0
        assert not any(t.title == "Alpha Private Acquisition Task" for t in tasks_beta)

        # 2. Memory Isolation
        memories_beta = (await db.execute(select(Memory).where(Memory.user_id == beta_id))).scalars().all()
        assert len(memories_beta) == 0
        assert not any("Alpha secret habit" in m.content for m in memories_beta)

        # 3. Documents Isolation
        docs_beta = (await db.execute(select(Document).where(Document.user_id == beta_id))).scalars().all()
        assert len(docs_beta) == 0
        assert not any(d.title == "Alpha Q3 Financial Model" for d in docs_beta)

        # 4. Conversations Isolation
        convs_beta = (await db.execute(select(Conversation).where(Conversation.user_id == beta_id))).scalars().all()
        assert len(convs_beta) == 0
        assert not any(c.title == "Alpha Confidential Meeting" for c in convs_beta)

        # 5. Messages Isolation
        msgs_beta = (await db.execute(select(Message).where(Message.user_id == beta_id))).scalars().all()
        assert len(msgs_beta) == 0
        assert not any("Alpha private communication" in m.content for m in msgs_beta)

        # 6. Calendar Events Isolation
        events_beta = (await db.execute(select(CalendarEvent).where(CalendarEvent.user_id == beta_id))).scalars().all()
        assert len(events_beta) == 0
        assert not any(e.title == "Alpha Board Strategy" for e in events_beta)

        # Direct IDOR protection test: Beta attempting to load Alpha's task directly
        idor_task = (await db.execute(
            select(Task).where(Task.id == task_alpha.id, Task.user_id == beta_id)
        )).scalars().first()
        assert idor_task is None, "CRITICAL: IDOR vulnerability detected! User Beta retrieved User Alpha task."

        # Direct IDOR protection test: Beta attempting to load Alpha's document directly
        idor_doc = (await db.execute(
            select(Document).where(Document.id == doc_alpha.id, Document.user_id == beta_id)
        )).scalars().first()
        assert idor_doc is None, "CRITICAL: IDOR vulnerability detected! User Beta retrieved User Alpha document."
