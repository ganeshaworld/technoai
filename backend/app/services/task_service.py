from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_
from backend.app.db.models import Task

class TaskService:
    @staticmethod
    async def list_tasks(
        db: AsyncSession,
        user_id: str,
        view: str = "all",
        status: Optional[str] = None,
        priority: Optional[str] = None
    ) -> List[Task]:
        now = datetime.now(timezone.utc)
        stmt = select(Task).where(Task.user_id == user_id)

        if status:
            stmt = stmt.where(Task.status == status)

        if priority:
            stmt = stmt.where(Task.priority == priority)

        if view == "today":
            start_today = datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=timezone.utc)
            end_today = start_today + timedelta(days=1)
            stmt = stmt.where(
                or_(
                    Task.due_date == None,
                    and_(Task.due_date >= start_today, Task.due_date < end_today)
                )
            ).where(Task.status != "completed")
        elif view == "upcoming":
            stmt = stmt.where(Task.due_date > now, Task.status != "completed")
        elif view == "overdue":
            stmt = stmt.where(Task.due_date < now, Task.status != "completed")
        elif view == "completed":
            stmt = stmt.where(Task.status == "completed")

        # Sort urgent/high first, then by due date
        stmt = stmt.order_by(Task.status.asc(), Task.due_date.asc().nulls_last())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def create_task(
        db: AsyncSession,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        priority: str = "medium",
        due_date: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        created_by_agent: str = "User"
    ) -> Task:
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
            status="todo",
            due_date=due_date,
            tags=tags or [],
            created_by_agent=created_by_agent
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def update_task(
        db: AsyncSession,
        task_id: str,
        user_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[datetime] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[Task]:
        stmt = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await db.execute(stmt)
        task = result.scalars().first()
        if not task:
            return None

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if status is not None:
            task.status = status
        if priority is not None:
            task.priority = priority
        if due_date is not None:
            task.due_date = due_date
        if tags is not None:
            task.tags = tags

        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def delete_task(db: AsyncSession, task_id: str, user_id: str) -> bool:
        stmt = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await db.execute(stmt)
        task = result.scalars().first()
        if not task:
            return False
        await db.delete(task)
        await db.commit()
        return True

    @staticmethod
    def extract_task_from_text(text: str) -> Optional[Dict[str, Any]]:
        """Parses natural language prompt for task title, priority, and timeframe."""
        lower = text.lower()
        priority = "medium"
        if "urgent" in lower or "asap" in lower:
            priority = "urgent"
        elif "high priority" in lower or "important" in lower:
            priority = "high"
        elif "low priority" in lower:
            priority = "low"

        due_date = None
        now = datetime.now(timezone.utc)
        if "tomorrow" in lower:
            due_date = now + timedelta(days=1)
        elif "next week" in lower:
            due_date = now + timedelta(days=7)
        elif "today" in lower:
            due_date = now.replace(hour=18, minute=0, second=0)

        # Clean title
        title = text
        for prefix in ["create a task to", "create task:", "remind me to", "add task", "todo:"]:
            if lower.startswith(prefix):
                title = text[len(prefix):].strip()
                break

        return {
            "title": title[:200],
            "priority": priority,
            "due_date": due_date
        }
