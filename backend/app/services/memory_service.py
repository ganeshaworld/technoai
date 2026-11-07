from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from backend.app.db.models import Memory

class MemoryService:
    @staticmethod
    async def get_user_memories(
        db: AsyncSession,
        user_id: str,
        category: Optional[str] = None
    ) -> List[Memory]:
        stmt = select(Memory).where(Memory.user_id == user_id, Memory.is_active == True)
        if category:
            stmt = stmt.where(Memory.category == category)
        stmt = stmt.order_by(Memory.is_pinned.desc(), Memory.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def add_memory(
        db: AsyncSession,
        user_id: str,
        category: str,
        content: str,
        importance_score: float = 1.0,
        is_pinned: bool = False
    ) -> Memory:
        mem = Memory(
            user_id=user_id,
            category=category,
            content=content,
            importance_score=importance_score,
            is_pinned=is_pinned,
            is_active=True
        )
        db.add(mem)
        await db.commit()
        await db.refresh(mem)
        return mem

    @staticmethod
    async def update_memory(
        db: AsyncSession,
        memory_id: str,
        user_id: str,
        content: Optional[str] = None,
        category: Optional[str] = None,
        is_pinned: Optional[bool] = None
    ) -> Optional[Memory]:
        stmt = select(Memory).where(Memory.id == memory_id, Memory.user_id == user_id)
        result = await db.execute(stmt)
        mem = result.scalars().first()
        if not mem:
            return None
        if content is not None:
            mem.content = content
        if category is not None:
            mem.category = category
        if is_pinned is not None:
            mem.is_pinned = is_pinned
        await db.commit()
        await db.refresh(mem)
        return mem

    @staticmethod
    async def delete_memory(db: AsyncSession, memory_id: str, user_id: str) -> bool:
        stmt = select(Memory).where(Memory.id == memory_id, Memory.user_id == user_id)
        result = await db.execute(stmt)
        mem = result.scalars().first()
        if not mem:
            return False
        await db.delete(mem)
        await db.commit()
        return True

    @staticmethod
    async def clear_all_memories(db: AsyncSession, user_id: str) -> int:
        stmt = delete(Memory).where(Memory.user_id == user_id)
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount

    @staticmethod
    async def retrieve_relevant_context(
        db: AsyncSession,
        user_id: str,
        query: str,
        limit: int = 5
    ) -> str:
        """
        Retrieves relevant memories and working habits formatted for injection into the system prompt.
        Uses keyword relevance and priority matching.
        """
        memories = await MemoryService.get_user_memories(db, user_id)
        if not memories:
            return "No prior user preferences recorded."

        query_terms = set(query.lower().split())
        scored_memories = []
        for m in memories:
            score = 1.0 if m.is_pinned else 0.5
            content_lower = m.content.lower()
            matches = sum(1 for term in query_terms if term in content_lower)
            score += matches * 0.8
            scored_memories.append((score, m))

        scored_memories.sort(key=lambda x: x[0], reverse=True)
        top_items = [f"[{m.category.upper()}]: {m.content}" for _, m in scored_memories[:limit]]
        return "\n".join(top_items)
