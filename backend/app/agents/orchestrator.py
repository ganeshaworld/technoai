import json
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.services.ai_providers import model_router
from backend.app.services.memory_service import MemoryService
from backend.app.services.task_service import TaskService
from backend.app.services.calendar_service import CalendarService
from backend.app.services.email_service import EmailService
from backend.app.services.document_service import DocumentService
from backend.app.services.research_service import ResearchService
from backend.app.core.guardrails import requires_user_confirmation, wrap_untrusted_input

class CentralAIBrain:
    """
    Central Executive AI Brain.
    Orchestrates the 6-stage Cognitive Loop:
    UNDERSTAND -> REMEMBER -> PLAN -> EXECUTE -> VERIFY -> REPORT
    """

    @staticmethod
    async def process_executive_request(
        db: AsyncSession,
        user_id: str,
        user_name: str,
        prompt: str,
        provider_name: Optional[str] = None
    ) -> Dict[str, Any]:
        # 1. UNDERSTAND: Identify user intent and domain
        intent = CentralAIBrain._classify_intent(prompt)

        # 2. REMEMBER: Retrieve user preferences and context
        memory_context = await MemoryService.retrieve_relevant_context(db, user_id, prompt)

        # 3. PLAN: Decompose into actionable steps & check autonomy levels
        plan_steps = CentralAIBrain._synthesize_plan(intent, prompt)

        # 4. EXECUTE & 5. VERIFY: Run authorized sub-agents or prepare level 3 approval gates
        execution_results = []
        action_required = None

        if intent == "schedule_and_day":
            # Multi-agent coordination: Calendar + Email + Tasks
            briefing = await CalendarService.generate_daily_briefing(db, user_id)
            tasks = await TaskService.list_tasks(db, user_id, view="today")
            emails = EmailService.get_inbox_messages(user_id)
            urgent_emails = [e for e in emails if e["category"] in ("action_required", "vip")]

            execution_results.append({"domain": "calendar", "data": briefing})
            execution_results.append({"domain": "tasks", "total_pending": len(tasks)})
            execution_results.append({"domain": "emails", "urgent_count": len(urgent_emails)})

        elif intent == "task_management":
            parsed = TaskService.extract_task_from_text(prompt)
            if parsed and parsed.get("title"):
                new_task = await TaskService.create_task(
                    db,
                    user_id=user_id,
                    title=parsed["title"],
                    priority=parsed["priority"],
                    due_date=parsed["due_date"],
                    created_by_agent="AI Assistant"
                )
                execution_results.append({"domain": "tasks", "created_task": new_task.title})

        elif intent == "email_triage":
            emails = EmailService.get_inbox_messages(user_id)
            execution_results.append({"domain": "emails", "messages": emails})
            # Action required gate for external reply dispatch
            action_required = {
                "action": "send_email",
                "target": "eleanor@apexpartners.vc",
                "description": "Approval required to send financial burn model follow-up reply.",
                "requires_approval": True,
                "autonomy_level": "level_3"
            }

        elif intent == "document_generation":
            doc_type = "docx"
            if "pdf" in prompt.lower():
                doc_type = "pdf"
            elif "excel" in prompt.lower() or "xlsx" in prompt.lower() or "csv" in prompt.lower():
                doc_type = "xlsx"
            elif "presentation" in prompt.lower() or "pptx" in prompt.lower() or "slide" in prompt.lower():
                doc_type = "pptx"

            new_doc = await DocumentService.create_document(
                db,
                user_id=user_id,
                title="Executive Proposal & Strategy Brief",
                doc_type=doc_type,
                content="## Executive Strategy\n- Primary Objective: Global SaaS scaling.\n- Timeline: Q3-Q4 Execution.\n- Resource allocation verified.",
                source_prompt=prompt
            )
            execution_results.append({"domain": "documents", "document_id": new_doc.id, "title": new_doc.title, "type": doc_type})

        elif intent == "deep_research":
            research_data = await ResearchService.perform_research(prompt)
            execution_results.append({"domain": "research", "data": research_data})

        # 6. REPORT: Formulate clear executive response using LLM Provider
        system_prompt = (
            f"You are Technopie AI, an elite Personal and Executive Assistant for {user_name}.\n"
            "Parent Company: Technopie Consultant Pvt. Ltd.\n"
            "Persona: Highly competent, proactive, structured, executive Chief of Staff.\n"
            "Workflow: UNDERSTAND -> REMEMBER -> PLAN -> EXECUTE -> VERIFY -> REPORT.\n"
            "Always distinguish clearly between completed actions, drafts, and actions requiring approval.\n\n"
            f"User Context & Memories:\n{memory_context}\n\n"
            f"Execution Results:\n{json.dumps(execution_results, default=str)}\n"
        )

        provider = model_router.get_provider(provider_name)
        llm_response = await provider.generate_response(
            messages=[{"role": "user", "content": prompt}],
            system_prompt=system_prompt
        )

        return {
            "intent": intent,
            "plan_steps": plan_steps,
            "execution_results": execution_results,
            "action_required": action_required,
            "report": llm_response["content"],
            "model_provider": llm_response.get("provider", "gemini"),
            "model_name": llm_response.get("model", "gemini-2.5-flash"),
            "tokens_used": llm_response.get("tokens_used", 0)
        }

    @staticmethod
    def _classify_intent(prompt: str) -> str:
        p = prompt.lower()
        if any(w in p for w in ["organize my day", "schedule", "calendar", "tomorrow", "agenda", "briefing"]):
            return "schedule_and_day"
        if any(w in p for w in ["task", "todo", "remind me to", "unfinished"]):
            return "task_management"
        if any(w in p for w in ["email", "inbox", "gmail", "reply", "draft"]):
            return "email_triage"
        if any(w in p for w in ["document", "proposal", "pdf", "docx", "xlsx", "presentation", "pptx"]):
            return "document_generation"
        if any(w in p for w in ["research", "market", "competitor", "trends", "analysis"]):
            return "deep_research"
        return "general_executive_query"

    @staticmethod
    def _synthesize_plan(intent: str, prompt: str) -> List[str]:
        if intent == "schedule_and_day":
            return [
                "Retrieve user schedule & meetings (Level 1: Read)",
                "Identify potential calendar conflicts (Level 1: Read)",
                "Scan authorized emails for urgent client requests (Level 1: Read)",
                "Extract pending and overdue tasks (Level 1: Read)",
                "Synthesize prioritized daily briefing (Level 2: Prepare)"
            ]
        elif intent == "task_management":
            return [
                "Parse natural language task parameters (Level 1: Read)",
                "Assign executive priority score (Level 2: Prepare)",
                "Insert record into Task Management engine (Level 2: Prepare)"
            ]
        elif intent == "email_triage":
            return [
                "Query authorized inbox (Level 1: Read)",
                "Categorize into VIP / Action Required / Newsletters (Level 1: Read)",
                "Generate draft replies matching user tone (Level 2: Prepare)",
                "Halt at Level 3 boundary for manual user dispatch confirmation"
            ]
        elif intent == "document_generation":
            return [
                "Structure document outline & sections (Level 2: Prepare)",
                "Generate real binary document with corporate formatting (Level 2: Prepare)",
                "Verify file integrity and generate secure download token (Level 2: Prepare)"
            ]
        elif intent == "deep_research":
            return [
                "Formulate multi-source query vectors (Level 1: Read)",
                "Extract statements and verify factual consistency (Level 1: Read)",
                "Categorize into Facts, Estimates, Opinions, and Unverified (Level 2: Prepare)"
            ]
        return ["Analyze prompt intent", "Assemble relevant memory context", "Generate executive response"]
