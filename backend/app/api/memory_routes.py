from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.db.models import User
from backend.app.core.security import get_current_user
from backend.app.services.memory_service import MemoryService

router = APIRouter(prefix="/memories", tags=["Personal Memory Management"])

class CreateMemoryRequest(BaseModel):
    category: str # personal, professional, preference, habit, goal
    content: str
    importance_score: Optional[float] = 1.0
    is_pinned: Optional[bool] = False

class UpdateMemoryRequest(BaseModel):
    content: Optional[str] = None
    category: Optional[str] = None
    is_pinned: Optional[bool] = None

@router.get("")
async def list_memories(
    category: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    memories = await MemoryService.get_user_memories(db, user.id, category)
    if not memories:
        # Seed initial executive habits for rich user experience
        m1 = await MemoryService.add_memory(
            db, user.id, "preference",
            "Prefers morning meetings strictly between 9:30 AM and 1:00 PM; no external calls on Friday afternoons.",
            is_pinned=True
        )
        m2 = await MemoryService.add_memory(
            db, user.id, "professional",
            "Active Role: Founder & Managing Director at Technopie AI. Prioritizes enterprise SaaS expansion.",
            is_pinned=True
        )
        m3 = await MemoryService.add_memory(
            db, user.id, "habit",
            "Prefers executive summaries with bulleted action items and explicit risk assessments.",
            is_pinned=False
        )
        memories = [m1, m2, m3]

    return [
        {
            "id": m.id,
            "category": m.category,
            "content": m.content,
            "importance_score": m.importance_score,
            "is_pinned": m.is_pinned,
            "created_at": m.created_at.isoformat()
        } for m in memories
    ]

@router.post("")
async def add_memory(
    payload: CreateMemoryRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    mem = await MemoryService.add_memory(
        db,
        user_id=user.id,
        category=payload.category,
        content=payload.content,
        importance_score=payload.importance_score or 1.0,
        is_pinned=payload.is_pinned or False
    )
    return {
        "id": mem.id,
        "category": mem.category,
        "content": mem.content,
        "is_pinned": mem.is_pinned
    }

@router.put("/{memory_id}")
async def update_memory(
    memory_id: str,
    payload: UpdateMemoryRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    updated = await MemoryService.update_memory(
        db,
        memory_id=memory_id,
        user_id=user.id,
        content=payload.content,
        category=payload.category,
        is_pinned=payload.is_pinned
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Memory item not found.")
    return {"status": "success", "id": updated.id}

@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    success = await MemoryService.delete_memory(db, memory_id, user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory item not found.")
    return {"status": "success", "message": "Memory permanently deleted."}

@router.delete("/clear/all")
async def clear_all(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    count = await MemoryService.clear_all_memories(db, user.id)
    return {"status": "success", "deleted_count": count}
