from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.app.db.models import CalendarEvent

class CalendarService:
    @staticmethod
    async def get_upcoming_events(
        db: AsyncSession,
        user_id: str,
        days_ahead: int = 7
    ) -> List[CalendarEvent]:
        now = datetime.now(timezone.utc)
        cutoff = now + timedelta(days=days_ahead)
        stmt = select(CalendarEvent).where(
            CalendarEvent.user_id == user_id,
            CalendarEvent.end_time >= now,
            CalendarEvent.start_time <= cutoff,
            CalendarEvent.status != "cancelled"
        ).order_by(CalendarEvent.start_time.asc())
        result = await db.execute(stmt)
        events = list(result.scalars().all())

        # If user has no events yet, provide default executive initial events
        if not events:
            tomorrow = now + timedelta(days=1)
            e1 = CalendarEvent(
                user_id=user_id,
                title="Executive Leadership Alignment",
                description="Review Q3 enterprise revenue targets and cross-functional deliverables.",
                start_time=tomorrow.replace(hour=9, minute=30, second=0, microsecond=0),
                end_time=tomorrow.replace(hour=10, minute=15, second=0, microsecond=0),
                location="Boardroom A / Zoom",
                meeting_link="https://meet.google.com/xyz-technopie",
                status="confirmed",
                ai_agenda_summary="1. Revenue review\n2. AI SaaS rollout schedule\n3. Hiring plan"
            )
            e2 = CalendarEvent(
                user_id=user_id,
                title="Investor Portfolio Review",
                description="Discussion with Series A investors regarding unit economics.",
                start_time=tomorrow.replace(hour=14, minute=0, second=0, microsecond=0),
                end_time=tomorrow.replace(hour=15, minute=0, second=0, microsecond=0),
                location="Virtual",
                status="confirmed",
                ai_agenda_summary="1. Customer acquisition cost analysis\n2. Expansion roadmap"
            )
            db.add_all([e1, e2])
            await db.commit()
            await db.refresh(e1)
            await db.refresh(e2)
            events = [e1, e2]

        return events

    @staticmethod
    async def create_event(
        db: AsyncSession,
        user_id: str,
        title: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        meeting_link: Optional[str] = None
    ) -> CalendarEvent:
        event = CalendarEvent(
            user_id=user_id,
            title=title,
            start_time=start_time,
            end_time=end_time,
            description=description,
            location=location,
            attendees=attendees or [],
            meeting_link=meeting_link,
            status="confirmed"
        )
        db.add(event)
        await db.commit()
        await db.refresh(event)
        return event

    @staticmethod
    async def detect_conflicts(
        db: AsyncSession,
        user_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[CalendarEvent]:
        stmt = select(CalendarEvent).where(
            CalendarEvent.user_id == user_id,
            CalendarEvent.status != "cancelled",
            CalendarEvent.start_time < end_time,
            CalendarEvent.end_time > start_time
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def generate_daily_briefing(db: AsyncSession, user_id: str) -> Dict[str, Any]:
        events = await CalendarService.get_upcoming_events(db, user_id, days_ahead=1)
        return {
            "date": datetime.now(timezone.utc).strftime("%A, %B %d, %Y"),
            "total_events": len(events),
            "events": [
                {
                    "title": e.title,
                    "time": f"{e.start_time.strftime('%I:%M %p')} - {e.end_time.strftime('%I:%M %p')}",
                    "location": e.location,
                    "agenda": e.ai_agenda_summary
                } for e in events
            ]
        }
