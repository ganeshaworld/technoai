import os
import json
import httpx
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any, List, Optional
from backend.app.config import settings

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Generate a complete non-streaming response."""
        pass

    @abstractmethod
    async def stream_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        """Stream response tokens."""
        pass

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.base_url = "https://api.openai.com/v1"

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("OpenAI API key is not configured.")
        
        formatted_messages = [{"role": "system", "content": system_prompt}] + messages
        payload: Dict[str, Any] = {
            "model": model or "gpt-4o-mini",
            "messages": formatted_messages,
            "temperature": temperature,
        }
        if tools:
            payload["tools"] = tools

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload
            )
            resp.raise_for_status()
            data = resp.json()
            choice = data["choices"][0]["message"]
            return {
                "content": choice.get("content", ""),
                "provider": "openai",
                "model": data.get("model", model),
                "tokens_used": data.get("usage", {}).get("total_tokens", 0),
                "tool_calls": choice.get("tool_calls", [])
            }

    async def stream_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        if not self.api_key:
            raise ValueError("OpenAI API key is not configured.")
        
        formatted_messages = [{"role": "system", "content": system_prompt}] + messages
        payload = {
            "model": model or "gpt-4o-mini",
            "messages": formatted_messages,
            "temperature": temperature,
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        try:
                            chunk = json.loads(line[6:])
                            delta = chunk["choices"][0]["delta"].get("content", "")
                            if delta:
                                yield delta
                        except Exception:
                            continue

class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GOOGLE_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("Google Gemini API key is not configured.")

        gemini_model = model or "gemini-2.5-flash"
        contents = []
        for m in messages:
            role = "user" if m["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": m["content"]}]})

        payload: Dict[str, Any] = {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": {"temperature": temperature}
        }

        url = f"{self.base_url}/models/{gemini_model}:generateContent?key={self.api_key}"
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            candidates = data.get("candidates", [])
            text = ""
            if candidates and "content" in candidates[0]:
                parts = candidates[0]["content"].get("parts", [])
                text = "".join(p.get("text", "") for p in parts)
            tokens = data.get("usageMetadata", {}).get("totalTokenCount", 0)
            return {
                "content": text,
                "provider": "gemini",
                "model": gemini_model,
                "tokens_used": tokens,
                "tool_calls": []
            }

    async def stream_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        # For simplicity and reliability in SSE streaming, yield full response or stream chunks
        res = await self.generate_response(messages, system_prompt, model, temperature)
        words = res["content"].split(" ")
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")

class AnthropicProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.base_url = "https://api.anthropic.com/v1"

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("Anthropic API key is not configured.")

        claude_model = model or "claude-3-5-sonnet-20241022"
        formatted_messages = []
        for m in messages:
            formatted_messages.append({"role": m["role"], "content": m["content"]})

        payload = {
            "model": claude_model,
            "system": system_prompt,
            "messages": formatted_messages,
            "max_tokens": 4096,
            "temperature": temperature,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.base_url}/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json=payload
            )
            resp.raise_for_status()
            data = resp.json()
            content_blocks = data.get("content", [])
            text = "".join(b.get("text", "") for b in content_blocks if b.get("type") == "text")
            tokens = data.get("usage", {}).get("input_tokens", 0) + data.get("usage", {}).get("output_tokens", 0)
            return {
                "content": text,
                "provider": "anthropic",
                "model": claude_model,
                "tokens_used": tokens,
                "tool_calls": []
            }

    async def stream_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        res = await self.generate_response(messages, system_prompt, model, temperature)
        words = res["content"].split(" ")
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")

class MockProvider(BaseLLMProvider):
    """
    Intelligent Executive Fallback & Demo Engine.
    Employs executive reasoning to analyze intent and return realistic, structured executive outputs
    when upstream API keys are not provided.
    """
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        last_message = messages[-1]["content"].lower() if messages else ""
        
        # Parse execution_results from system_prompt if available
        exec_results = []
        if "Execution Results:\n" in system_prompt:
            try:
                raw_json = system_prompt.split("Execution Results:\n")[1].strip()
                exec_results = json.loads(raw_json)
            except Exception:
                exec_results = []

        # Check for dynamic execution results first
        for item in exec_results:
            domain = item.get("domain")
            action = item.get("action")

            if domain == "memory" and action == "stored":
                fact = item.get("fact", "your preference")
                content = (
                    f"### 🧠 Preference Stored\n\n"
                    f"I have committed this to your persistent executive memory bank:\n"
                    f"> **\"{fact}\"**\n\n"
                    f"I will strictly respect this preference across all future conversations."
                )
                return {"content": content, "provider": "mock", "model": "technopie-mock-v1", "tokens_used": 60, "tool_calls": []}

            elif domain == "memory" and action == "recalled":
                facts = item.get("facts", [])
                matched = [f for f in facts if "language" in f.lower() or "english" in f.lower() or "hindi" in f.lower()]
                pref_text = matched[0] if matched else "English"
                content = (
                    f"### 🧠 Recalled Preference\n\n"
                    f"According to your personal memory bank, your preferred language is **{pref_text}**.\n\n"
                    f"I will ensure all future briefings and drafts are formatted accordingly."
                )
                return {"content": content, "provider": "mock", "model": "technopie-mock-v1", "tokens_used": 65, "tool_calls": []}

            elif domain == "tasks" and action == "created":
                title = item.get("task_title", "New Task")
                priority = item.get("priority", "medium").upper()
                due = item.get("due_date", "Tomorrow")
                content = (
                    f"### 📋 Task Created Successfully\n\n"
                    f"I have added the task to your deliverables:\n"
                    f"- **Title:** {title}\n"
                    f"- **Priority:** {priority}\n"
                    f"- **Due Date:** {due}\n\n"
                    f"You can view and manage it on your Tasks board."
                )
                return {"content": content, "provider": "mock", "model": "technopie-mock-v1", "tokens_used": 75, "tool_calls": []}

            elif domain == "tasks" and action == "analyzed":
                tasks = item.get("task_list", [])
                lines = []
                for idx, t in enumerate(tasks[:5], 1):
                    lines.append(f"{idx}. **{t['title']}** [{t['priority'].upper()}] - Status: {t['status']}")
                task_lines = "\n".join(lines) if lines else "No pending tasks recorded."
                content = (
                    f"### 📋 Priority & Task Management Report\n\n"
                    f"I have audited your active task board and cross-referenced deadlines:\n\n"
                    f"{task_lines}\n\n"
                    f"**Recommendation:** Focus first on high and urgent deliverables before proceeding to lower-priority items."
                )
                return {"content": content, "provider": "mock", "model": "technopie-mock-v1", "tokens_used": 150, "tool_calls": []}

            elif domain == "research":
                content = (
                    "### 🔍 Competitive Intelligence: Top 5 AI Assistant SaaS Competitors\n\n"
                    "I have synthesized a multi-source comparative analysis across five leading executive AI assistant platforms:\n\n"
                    "1. **Motion (usemotion.com):** Specializes in algorithmic calendar time-blocking and automated schedule recovery.\n"
                    "2. **Superhuman AI:** High-speed executive email triage, thread prioritization, and instant drafting.\n"
                    "3. **Lindsa / Lindy.ai:** Autonomous personal agents for scheduling, email workflows, and integrations.\n"
                    "4. **Otter.ai:** AI meeting assistant focused on automated transcription, action-item extraction, and executive summaries.\n"
                    "5. **Microsoft Copilot for M365:** Enterprise assistant embedded across Word, Excel, Teams, and Outlook.\n\n"
                    "**Epistemic Analysis:**\n"
                    "- **Verified Fact:** Strict Level 3 human approval boundaries prevent unauthorized outbound email dispatch across enterprise platforms.\n"
                    "- **Estimate:** Executive assistant adoption yields 25%–38% time savings on routine coordination.\n"
                    "- **Expert Opinion:** Unified executive assistants with persistent memory will replace single-purpose productivity apps by 2028."
                )
                return {"content": content, "provider": "mock", "model": "technopie-mock-v1", "tokens_used": 320, "tool_calls": []}

        # Fallback keyword matching
        if any(w in last_message for w in ["schedule", "tomorrow", "calendar", "agenda", "meeting"]):
            content = (
                "### 📅 Executive Daily Briefing & Schedule Analysis\n\n"
                "I have reviewed your calendar, extracted priorities, and analyzed upcoming commitments:\n\n"
                "**1. Schedule for Tomorrow:**\n"
                "- **09:30 AM – 10:15 AM:** Q3 Strategy Alignment with Executive Committee *(Zoom)*\n"
                "- **11:30 AM – 12:15 PM:** Investor Briefing & Financial Projections Review\n"
                "- **02:00 PM – 03:00 PM:** Focus Time: Review Enterprise SaaS Proposal & Security Audit\n"
                "- **04:30 PM – 05:00 PM:** Weekly 1:1 Check-in with Chief of Product\n\n"
                "**2. Key Attention Items:**\n"
                "- ⚠️ **Conflict Alert:** A tentative lunch meeting at 12:45 PM overlaps with travel time before your 2:00 PM deep work block.\n"
                "- ✉️ **Pending Reply:** Awaiting your approval to send follow-up emails regarding the AI adoption roadmap.\n\n"
                "Would you like me to reschedule the 12:45 PM tentative slot or prepare talking points for the 9:30 AM alignment call?"
            )
        elif any(w in last_message for w in ["email", "inbox", "gmail", "reply"]):
            content = (
                "### ✉️ Executive Email Intelligence\n\n"
                "I have scanned your authorized inbox and categorized recent communications:\n\n"
                "1. **VIP Client — Apex Ventures:** Requested updated financial model by tomorrow noon.\n"
                "   - *Action:* Draft reply prepared with attached Q3 metrics.\n"
                "2. **Legal Counsel:** Sent revised NDA for European acquisition.\n"
                "   - *Action:* Marked for your direct sign-off.\n"
                "3. **Vendor Renewal Notice:** AWS Enterprise contract review due in 5 days.\n\n"
                "> 🔒 *Safety Gate:* Sending external replies requires your explicit approval. You can review and confirm drafts in the Emails workspace."
            )
        elif any(w in last_message for w in ["document", "proposal", "report", "docx", "pdf", "generate"]):
            content = (
                "### 📄 Document Ready for Generation\n\n"
                "I have structured the requested executive document based on your parameters:\n\n"
                "- **Title:** Technopie AI Enterprise Strategy Document\n"
                "- **Format:** Microsoft Word (.docx) & Executive PDF\n"
                "- **Sections:** Executive Summary, Architecture Breakdown, Market Opportunity, Financial Forecast\n\n"
                "You can generate and download the completed file directly using the Document Assistant."
            )
        else:
            content = (
                "Hello Alexander. I am your **Technopie AI Executive Assistant**.\n\n"
                "I am actively monitoring your calendar, prioritizing pending tasks, and ready to assist with:\n\n"
                "- **Executive Scheduling:** Analyzing calendar conflicts and optimizing your day\n"
                "- **Inbox Management:** Categorizing VIP emails and preparing professional draft replies\n"
                "- **Task Automation:** Converting instructions into prioritized actions\n"
                "- **Deep Research & Documents:** Producing proposals, reports, and strategic briefs\n\n"
                "How would you like to direct your assistant right now?"
            )

        return {
            "content": content,
            "provider": "mock",
            "model": "technopie-mock-v1",
            "tokens_used": 280,
            "tool_calls": []
        }

    async def stream_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        res = await self.generate_response(messages, system_prompt, model, temperature)
        words = res["content"].split(" ")
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")

class AIModelRouter:
    """
    Central router that dynamically selects the optimal model provider
    based on task type, availability, and fallback cascading.
    """
    def __init__(self):
        self.openai = OpenAIProvider()
        self.gemini = GeminiProvider()
        self.anthropic = AnthropicProvider()
        self.mock = MockProvider()

    def get_provider(self, requested_provider: Optional[str] = None) -> BaseLLMProvider:
        prov = (requested_provider or settings.DEFAULT_AI_PROVIDER).lower()
        if prov == "gemini" and settings.GOOGLE_API_KEY:
            return self.gemini
        elif prov == "openai" and settings.OPENAI_API_KEY:
            return self.openai
        elif prov == "anthropic" and settings.ANTHROPIC_API_KEY:
            return self.anthropic
        
        # Fallback cascade: check if any configured
        if settings.GOOGLE_API_KEY:
            return self.gemini
        if settings.OPENAI_API_KEY:
            return self.openai
        if settings.ANTHROPIC_API_KEY:
            return self.anthropic
        
        # Default to intelligent mock provider
        return self.mock

model_router = AIModelRouter()
