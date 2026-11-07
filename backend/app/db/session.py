import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import event, text
from backend.app.config import settings

logger = logging.getLogger("technopie.ai.database")

def get_normalized_database_url(url: str) -> str:
    """Normalize database URL for async drivers (e.g. Supabase / RDS / PostgreSQL)."""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql://") and not url.startswith("postgresql+"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url

normalized_url = get_normalized_database_url(settings.DATABASE_URL)
is_sqlite = "sqlite" in normalized_url
is_postgres = "postgres" in normalized_url

engine_kwargs = {
    "echo": False,
    "future": True,
}

if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
elif is_postgres:
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_recycle"] = 3600

engine = create_async_engine(normalized_url, **engine_kwargs)

@event.listens_for(engine.sync_engine, "connect")
def configure_dbapi_connection(dbapi_connection, connection_record):
    if is_sqlite:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=AsyncSession
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    async with engine.begin() as conn:
        if is_postgres:
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                logger.info("pgvector extension verified or enabled successfully.")
            except Exception as e:
                logger.warning(
                    "pgvector extension check bypassed (deployment environment may lack vector extension or superuser): %s",
                    str(e)
                )
        await conn.run_sync(Base.metadata.create_all)
