import json
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.db.session import get_db
from backend.app.db.models import User, Conversation, Message, UserProfile
from backend.app.core.security import get_current_user
from backend.app.agents.orchestrator import CentralAIBrain
from backend.app.services.ai_providers import model_router
from backend.app.config import settings

router = APIRouter(prefix="/chat", tags=["AI Conversations & Assistant"])

@router.get("/provider-status")
async def get_provider_status(user: User = Depends(get_current_user)):
    return {
        "default_provider": settings.DEFAULT_AI_PROVIDER,
        "environment": settings.ENVIRONMENT,
        "allow_mock_fallback": settings.ALLOW_MOCK_FALLBACK,
        "providers": {
            "gemini": {
                "active": True,
                "configured": bool(settings.GOOGLE_API_KEY and settings.GOOGLE_API_KEY.strip()),
                "fast_model": settings.DEFAULT_FAST_MODEL,
                "reasoning_model": settings.DEFAULT_REASONING_MODEL,
                "timeout_seconds": settings.AI_REQUEST_TIMEOUT_SECONDS,
                "max_retries": settings.AI_MAX_RETRIES
            },
            "openai": {
                "active": False,
                "configured": bool(settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip()),
                "model": "gpt-4o-mini"
            },
            "anthropic": {
                "active": False,
                "configured": bool(settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY.strip()),
                "model": "claude-3-5-sonnet-20241022"
            }
        }
    }

class CreateConversationRequest(BaseModel):
    title: Optional[str] = "Executive Session"
    agent_type: Optional[str] = "general_assistant"

class SendMessageRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str
    provider: Optional[str] = None
    model: Optional[str] = None

@router.get("/conversations")
async def list_conversations(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Conversation).where(
        Conversation.user_id == user.id,
        Conversation.is_archived == False
    ).order_by(Conversation.updated_at.desc())
    result = await db.execute(stmt)
    convs = list(result.scalars().all())

    if not convs:
        # Create initial default conversation
        conv = Conversation(
            user_id=user.id,
            title="Strategic Executive Planning",
            agent_type="general_assistant"
        )
        db.add(conv)
        await db.commit()
        await db.refresh(conv)

        # Add initial assistant welcome message
        welcome_msg = Message(
            conversation_id=conv.id,
            user_id=user.id,
            sender_role="assistant",
            content="Welcome to Technopie AI. I am your Executive Assistant. I am monitoring your schedule, emails, and active tasks. How may I assist your productivity today?",
            model_provider="gemini",
            model_name="gemini-2.5-flash"
        )
        db.add(welcome_msg)
        await db.commit()
        convs = [conv]

    return [
        {
            "id": c.id,
            "title": c.title,
            "agent_type": c.agent_type,
            "is_pinned": c.is_pinned,
            "updated_at": c.updated_at.isoformat()
        } for c in convs
    ]

@router.post("/conversations")
async def create_conversation(
    payload: CreateConversationRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    conv = Conversation(
        user_id=user.id,
        title=payload.title or "Executive Session",
        agent_type=payload.agent_type or "general_assistant"
    )
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return {"id": conv.id, "title": conv.title, "agent_type": conv.agent_type}

@router.get("/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Message).where(
        Message.conversation_id == conversation_id,
        Message.user_id == user.id
    ).order_by(Message.created_at.asc())
    result = await db.execute(stmt)
    messages = list(result.scalars().all())
    return [
        {
            "id": m.id,
            "sender_role": m.sender_role,
            "content": m.content,
            "model_provider": m.model_provider,
            "model_name": m.model_name,
            "tool_calls": m.tool_calls,
            "action_items": m.action_items,
            "created_at": m.created_at.isoformat()
        } for m in messages
    ]

@router.post("/message")
async def send_message(
    payload: SendMessageRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    conv_id = payload.conversation_id
    if not conv_id:
        conv = Conversation(user_id=user.id, title="Executive Session")
        db.add(conv)
        await db.flush()
        conv_id = conv.id

    # Get user profile name
    stmt_prof = select(UserProfile).where(UserProfile.user_id == user.id)
    profile = (await db.execute(stmt_prof)).scalars().first()
    user_name = profile.full_name if profile else "Executive"

    # Save user message
    user_msg = Message(
        conversation_id=conv_id,
        user_id=user.id,
        sender_role="user",
        content=payload.message
    )
    db.add(user_msg)
    await db.flush()

    # Process via Central AI Brain
    brain_res = await CentralAIBrain.process_executive_request(
        db=db,
        user_id=user.id,
        user_name=user_name,
        prompt=payload.message,
        provider_name=payload.provider
    )

    # Save assistant message
    asst_msg = Message(
        conversation_id=conv_id,
        user_id=user.id,
        sender_role="assistant",
        content=brain_res["report"],
        model_provider=brain_res["model_provider"],
        model_name=brain_res["model_name"],
        tokens_used=brain_res["tokens_used"],
        tool_calls=brain_res["plan_steps"],
        action_items=[brain_res["action_required"]] if brain_res.get("action_required") else []
    )
    db.add(asst_msg)
    await db.commit()
    await db.refresh(asst_msg)

    return {
        "id": asst_msg.id,
        "conversation_id": conv_id,
        "sender_role": "assistant",
        "content": asst_msg.content,
        "model_provider": asst_msg.model_provider,
        "model_name": asst_msg.model_name,
        "plan_steps": brain_res["plan_steps"],
        "action_required": brain_res["action_required"],
        "created_at": asst_msg.created_at.isoformat()
    }
