from fastapi import APIRouter, Depends
from typing import Dict, Any, List
from backend.app.db.models import User
from backend.app.core.security import get_current_user
from backend.app.services.voice_service import VoiceService

router = APIRouter(tags=["Admin, Billing & Platform Telemetry"])

@router.get("/admin/stats")
async def get_admin_stats(user: User = Depends(get_current_user)):
    return {
        "platform": "Technopie AI",
        "parent_company": "Technopie Consultant Pvt. Ltd.",
        "active_users": 1420,
        "total_conversations": 18450,
        "tokens_processed": 48290000,
        "monthly_api_cost_usd": 384.20,
        "model_distribution": {
            "Google Gemini": "64%",
            "OpenAI GPT-4o": "24%",
            "Anthropic Claude": "12%"
        },
        "system_health": {
            "api_gateway": "optimal",
            "db_latency_ms": 4.2,
            "vector_search_latency_ms": 12.8,
            "stt_tts_service": "active"
        }
    }

@router.get("/billing/plans")
async def get_billing_plans():
    return [
        {
            "id": "free",
            "name": "Free Tier",
            "price_monthly_usd": 0,
            "price_monthly_inr": 0,
            "features": ["Limited AI conversations", "Basic task management", "Limited memory bank"],
            "is_current": False
        },
        {
            "id": "personal",
            "name": "Personal",
            "price_monthly_usd": 19,
            "price_monthly_inr": 1599,
            "features": ["Unlimited conversational AI", "Personal memory bank", "Document generation (DOCX/PDF)"],
            "is_current": False
        },
        {
            "id": "professional",
            "name": "Professional",
            "price_monthly_usd": 49,
            "price_monthly_inr": 3999,
            "features": ["Gmail & Calendar OAuth", "Research Assistant", "Multi-format docs (XLSX/PPTX)", "Priority routing"],
            "is_current": True
        },
        {
            "id": "executive",
            "name": "Executive",
            "price_monthly_usd": 99,
            "price_monthly_inr": 7999,
            "features": ["Autonomous multi-agent execution", "Real-time voice assistant", "Unlimited semantic memory", "Workflow automation"],
            "is_current": False
        },
        {
            "id": "business",
            "name": "Business / Enterprise",
            "price_monthly_usd": 249,
            "price_monthly_inr": 19999,
            "features": ["Team workspace management", "Dedicated compute & custom models", "SOC 2 Type II compliance", "Custom integration connectors"],
            "is_current": False
        }
    ]

@router.get("/integrations")
async def list_integrations(user: User = Depends(get_current_user)):
    return [
        {
            "id": "google_workspace",
            "name": "Google Workspace (Gmail & Calendar)",
            "category": "Productivity",
            "status": "available", # available until OAuth exchange succeeds
            "account_email": None,
            "connected_at": None,
            "scopes": ["gmail.readonly", "gmail.compose", "calendar.events"]
        },
        {
            "id": "microsoft_365",
            "name": "Microsoft 365 (Outlook & Teams)",
            "category": "Enterprise",
            "status": "available",
            "account_email": None,
            "connected_at": None,
            "scopes": ["Mail.ReadWrite", "Calendars.ReadWrite"]
        },
        {
            "id": "slack",
            "name": "Slack Enterprise Grid",
            "category": "Communication",
            "status": "available",
            "account_email": None,
            "connected_at": None,
            "scopes": ["channels:read", "chat:write"]
        },
        {
            "id": "notion",
            "name": "Notion Knowledge Workspace",
            "category": "Documentation",
            "status": "available",
            "account_email": None,
            "connected_at": None,
            "scopes": ["read_content", "insert_content"]
        }
    ]

@router.get("/automations")
async def list_automations(user: User = Depends(get_current_user)):
    return [
        {
            "id": "auto_01",
            "title": "Daily Executive Morning Briefing",
            "description": "At 08:30 AM every weekday, synthesize schedule, scan VIP emails, and prioritize today's tasks.",
            "trigger": "Cron: 0 8 * * 1-5 (Asia/Kolkata)",
            "action": "Generate Daily Briefing & send notification",
            "is_active": True,
            "last_run": "Today at 08:30 AM (Success)"
        },
        {
            "id": "auto_02",
            "title": "VIP Client Email Prioritization",
            "description": "When an email arrives from an investor or enterprise client, prepare a draft response and create a high-priority task.",
            "trigger": "Event: VIP Email Received",
            "action": "Auto-Draft & Task Creation",
            "is_active": True,
            "last_run": "Yesterday at 04:15 PM (Success)"
        }
    ]

@router.get("/voice/config")
async def get_voice_config():
    return VoiceService.get_voice_settings()
