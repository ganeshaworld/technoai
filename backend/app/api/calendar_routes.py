from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.db.models import User
from backend.app.core.security import get_current_user
from backend.app.services.calendar_service import CalendarService

router = APIRouter(prefix="/calendar", tags=["Calendar & Scheduling"])

class CreateEventRequest(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    attendees: Optional[List[str]] = []
    meeting_link: Optional[str] = None

@router.get("/events")
async def list_events(
    days: int = 7,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    events = await CalendarService.get_upcoming_events(db, user.id, days_ahead=days)
    return [
        {
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "start_time": e.start_time.isoformat(),
            "end_time": e.end_time.isoformat(),
            "location": e.location,
            "meeting_link": e.meeting_link,
            "status": e.status,
            "agenda": e.ai_agenda_summary
        } for e in events
    ]

@router.post("/events")
async def create_event(
    payload: CreateEventRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check for conflicts
    conflicts = await CalendarService.detect_conflicts(db, user.id, payload.start_time, payload.end_time)
    has_conflicts = len(conflicts) > 0

    event = await CalendarService.create_event(
        db,
        user_id=user.id,
        title=payload.title,
        start_time=payload.start_time,
        end_time=payload.end_time,
        description=payload.description,
        location=payload.location,
        attendees=payload.attendees,
        meeting_link=payload.meeting_link
    )
    return {
        "id": event.id,
        "title": event.title,
        "has_conflicts": has_conflicts,
        "conflict_count": len(conflicts),
        "status": event.status
    }

@router.get("/briefing")
async def get_daily_briefing(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await CalendarService.generate_daily_briefing(db, user.id)
