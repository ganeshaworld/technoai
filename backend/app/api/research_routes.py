from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from backend.app.db.models import User
from backend.app.core.security import get_current_user
from backend.app.services.research_service import ResearchService

router = APIRouter(prefix="/research", tags=["Deep Research Assistant"])

class ResearchQueryRequest(BaseModel):
    query: str
    depth: Optional[str] = "comprehensive"

@router.post("/query")
async def execute_research(
    payload: ResearchQueryRequest,
    user: User = Depends(get_current_user)
):
    return await ResearchService.perform_research(payload.query, payload.depth or "comprehensive")
