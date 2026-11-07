from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.db.models import User
from backend.app.core.security import get_current_user
from backend.app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Executive Task Management"])

class CreateTaskRequest(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "medium" # low, medium, high, urgent
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = []

class UpdateTaskRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None # todo, in_progress, completed, cancelled
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None

@router.get("")
async def list_tasks(
    view: str = "all", # today, upcoming, overdue, completed, all
    status: Optional[str] = None,
    priority: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tasks = await TaskService.list_tasks(db, user.id, view, status, priority)
    if not tasks and view == "all":
        # Initialize default executive tasks
        now = datetime.now(timezone.utc)
        t1 = await TaskService.create_task(
            db, user.id,
            title="Finalize Master Service Agreement (MSA) for Cloud Migration",
            description="Review cybersecurity indemnification clause with external legal counsel.",
            priority="urgent",
            due_date=now.replace(hour=17, minute=0, second=0),
            tags=["Legal", "Contracts"],
            created_by_agent="AI Assistant"
        )
        t2 = await TaskService.create_task(
            db, user.id,
            title="Approve Q3 Financial Variance Report",
            description="Examine departmental cloud computing expenses and model inference costs.",
            priority="high",
            due_date=now + timedelta(days=1),
            tags=["Finance", "Executive"],
            created_by_agent="User"
        )
        t3 = await TaskService.create_task(
            db, user.id,
            title="Review Autonomous Agent Autonomy Guardrails",
            description="Ensure Level 3 actions strictly mandate interactive authorization cards.",
            priority="medium",
            due_date=now + timedelta(days=3),
            tags=["Security", "AI"],
            created_by_agent="AI Assistant"
        )
        tasks = [t1, t2, t3]

    return [
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "status": t.status,
            "priority": t.priority,
            "due_date": t.due_date.isoformat() if t.due_date else None,
            "tags": t.tags,
            "created_by_agent": t.created_by_agent,
            "created_at": t.created_at.isoformat()
        } for t in tasks
    ]

@router.post("")
async def create_task(
    payload: CreateTaskRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    task = await TaskService.create_task(
        db,
        user_id=user.id,
        title=payload.title,
        description=payload.description,
        priority=payload.priority or "medium",
        due_date=payload.due_date,
        tags=payload.tags or [],
        created_by_agent="User"
    )
    return {
        "id": task.id,
        "title": task.title,
        "status": task.status,
        "priority": task.priority
    }

@router.patch("/{task_id}")
async def update_task(
    task_id: str,
    payload: UpdateTaskRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    task = await TaskService.update_task(
        db,
        task_id=task_id,
        user_id=user.id,
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        due_date=payload.due_date,
        tags=payload.tags
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return {"status": "success", "id": task.id, "new_status": task.status}

@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    success = await TaskService.delete_task(db, task_id, user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found.")
    return {"status": "success", "message": "Task deleted."}
