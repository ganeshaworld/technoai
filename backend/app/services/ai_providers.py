import os
import json
import time
import asyncio
import logging
import httpx
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any, List, Optional
from backend.app.config import settings

logger = logging.getLogger("technopie.ai.provider")

# ==============================================================================
# Structured AI Provider Exceptions
# ==============================================================================

class AIProviderError(Exception):
    """Base exception for all AI Provider errors."""
    def __init__(
        self,
        message: str,
        provider: str = "unknown",
        status_code: int = 500,
        retryable: bool = False
    ):
        super().__init__(message)
        self.message = message
        self.provider = provider
        self.status_code = status_code
        self.retryable = retryable

    def __str__(self) -> str:
        return f"[{self.provider.upper()}] {self.message} (HTTP {self.status_code})"


class AIProviderMissingKeyError(AIProviderError):
    """Raised when an API key is required but missing from environment."""
    def __init__(self, provider: str = "gemini", message: Optional[str] = None):
        env_var_name = "GOOGLE_API_KEY" if provider.lower() == "gemini" else f"{provider.upper()}_API_KEY"
        msg = (
            message or
            f"AI Provider Configuration Error: {env_var_name} is not configured "
            f"in environment variables. Please set {env_var_name} to enable real "
            f"{provider.capitalize()} assistant capabilities."
        )
        super().__init__(message=msg, provider=provider, status_code=503, retryable=False)


class AIProviderTimeoutError(AIProviderError):
    """Raised when an AI Provider API call times out after all retries."""
    def __init__(self, provider: str = "gemini", timeout_seconds: float = 30.0):
        super().__init__(
            message=f"AI Provider Timeout: {provider.capitalize()} API did not respond within {timeout_seconds}s limit after all retry attempts.",
            provider=provider,
            status_code=504,
            retryable=True
        )


class AIProviderRateLimitError(AIProviderError):
    """Raised on HTTP 429 quota/rate limit error."""
    def __init__(self, provider: str = "gemini", detail: str = ""):
        msg = f"AI Provider Rate Limit / Quota Exceeded: {provider.capitalize()} request limit reached."
        if detail:
            msg += f" Details: {detail}"
        super().__init__(message=msg, provider=provider, status_code=429, retryable=True)


class AIProviderAPIError(AIProviderError):
    """Raised on upstream HTTP 4xx/5xx API errors."""
    def __init__(self, provider: str, status_code: int, detail: str = ""):
        super().__init__(
            message=f"AI Provider API Error ({provider.capitalize()} status {status_code}): {detail}",
            provider=provider,
            status_code=status_code,
            retryable=(status_code in (500, 502, 503, 504))
        )


# ==============================================================================
# Base LLM Provider Interface
# ==============================================================================

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


# ==============================================================================
# Google Gemini Provider (Primary Active Model in Phase 2A)
# ==============================================================================

class GeminiProvider(BaseLLMProvider):
    """
    Production Google Gemini Provider using Google Generative Language v1beta API.
    Features:
    - Environment variable authentication
    - Configurable timeout and exponential backoff retry loop
    - Token usage tracking and structured logging
    - Explicit non-silent error propagation
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GOOGLE_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.provider_name = "gemini"

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        if not self.api_key or not self.api_key.strip():
            raise AIProviderMissingKeyError(self.provider_name)

        gemini_model = model or settings.DEFAULT_FAST_MODEL
        contents = []
        for m in messages:
            role = "user" if m.get("role") == "user" else "model"
            contents.append({"role": role, "parts": [{"text": m.get("content", "")}]})

        payload: Dict[str, Any] = {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": {"temperature": temperature}
        }
        if tools:
            payload["tools"] = tools

        url = f"{self.base_url}/models/{gemini_model}:generateContent?key={self.api_key}"
        timeout = settings.AI_REQUEST_TIMEOUT_SECONDS
        max_retries = settings.AI_MAX_RETRIES
        backoff_factor = settings.AI_RETRY_BACKOFF_FACTOR

        for attempt in range(1, max_retries + 1):
            start_time = time.time()
            try:
                logger.info(
                    "Gemini API request: model=%s, attempt=%d/%d, timeout=%.1fs",
                    gemini_model, attempt, max_retries, timeout
                )
                async with httpx.AsyncClient(timeout=timeout) as client:
                    resp = await client.post(url, json=payload)
                    elapsed = time.time() - start_time

                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        text = ""
                        tool_calls = []
                        if candidates:
                            cand = candidates[0]
                            content = cand.get("content", {})
                            parts = content.get("parts", [])
                            for part in parts:
                                if "text" in part:
                                    text += part["text"]
                                elif "functionCall" in part:
                                    tool_calls.append(part["functionCall"])

                        usage = data.get("usageMetadata", {})
                        total_tokens = usage.get("totalTokenCount", 0)
                        prompt_tokens = usage.get("promptTokenCount", 0)
                        cand_tokens = usage.get("candidatesTokenCount", 0)

                        logger.info(
                            "Gemini API success in %.2fs: total_tokens=%d (prompt=%d, completion=%d)",
                            elapsed, total_tokens, prompt_tokens, cand_tokens
                        )
                        return {
                            "content": text,
                            "provider": self.provider_name,
                            "model": gemini_model,
                            "tokens_used": total_tokens,
                            "prompt_tokens": prompt_tokens,
                            "completion_tokens": cand_tokens,
                            "tool_calls": tool_calls
                        }

                    # Non-200 responses
                    status_code = resp.status_code
                    error_text = resp.text
                    try:
                        err_json = resp.json().get("error", {})
                        detail = err_json.get("message", error_text)
                    except Exception:
                        detail = error_text

                    if status_code == 429:
                        if attempt < max_retries:
                            wait_time = backoff_factor ** attempt
                            logger.warning(
                                "Gemini quota/rate limit (429). Retrying in %.2fs (attempt %d/%d)...",
                                wait_time, attempt, max_retries
                            )
                            await asyncio.sleep(wait_time)
                            continue
                        raise AIProviderRateLimitError(self.provider_name, detail)

                    elif status_code in (500, 502, 503, 504):
                        if attempt < max_retries:
                            wait_time = backoff_factor ** attempt
                            logger.warning(
                                "Gemini upstream server error (%d). Retrying in %.2fs (attempt %d/%d)...",
                                status_code, wait_time, attempt, max_retries
                            )
                            await asyncio.sleep(wait_time)
                            continue
                        raise AIProviderAPIError(self.provider_name, status_code, detail)

                    elif status_code in (400, 401, 403):
                        # Client-side configuration errors (e.g. invalid API key or model name)
                        logger.error("Gemini client error (%d): %s", status_code, detail)
                        raise AIProviderAPIError(self.provider_name, status_code, detail)

                    else:
                        raise AIProviderAPIError(self.provider_name, status_code, detail)

            except httpx.TimeoutException:
                elapsed = time.time() - start_time
                if attempt < max_retries:
                    wait_time = backoff_factor ** attempt
                    logger.warning(
                        "Gemini request timed out after %.2fs. Retrying in %.2fs (attempt %d/%d)...",
                        elapsed, wait_time, attempt, max_retries
                    )
                    await asyncio.sleep(wait_time)
                    continue
                raise AIProviderTimeoutError(self.provider_name, timeout)

            except httpx.NetworkError as net_err:
                if attempt < max_retries:
                    wait_time = backoff_factor ** attempt
                    logger.warning(
                        "Gemini network error: %s. Retrying in %.2fs...",
                        str(net_err), wait_time
                    )
                    await asyncio.sleep(wait_time)
                    continue
                raise AIProviderAPIError(
                    self.provider_name,
                    status_code=503,
                    detail=f"Network connectivity error contacting Gemini API: {str(net_err)}"
                )

        raise AIProviderError(
            message=f"Gemini API request failed after {max_retries} attempts.",
            provider=self.provider_name,
            status_code=500
        )

    async def stream_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        if not self.api_key or not self.api_key.strip():
            raise AIProviderMissingKeyError(self.provider_name)

        gemini_model = model or settings.DEFAULT_FAST_MODEL
        contents = []
        for m in messages:
            role = "user" if m.get("role") == "user" else "model"
            contents.append({"role": role, "parts": [{"text": m.get("content", "")}]})

        payload = {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": {"temperature": temperature}
        }
        url = f"{self.base_url}/models/{gemini_model}:streamGenerateContent?alt=sse&key={self.api_key}"
        timeout = settings.AI_REQUEST_TIMEOUT_SECONDS

        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream("POST", url, json=payload) as resp:
                if resp.status_code != 200:
                    raw_err = await resp.aread()
                    raise AIProviderAPIError(self.provider_name, resp.status_code, raw_err.decode("utf-8", errors="ignore"))

                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if not data_str:
                            continue
                        try:
                            chunk = json.loads(data_str)
                            candidates = chunk.get("candidates", [])
                            if candidates:
                                parts = candidates[0].get("content", {}).get("parts", [])
                                for p in parts:
                                    t = p.get("text", "")
                                    if t:
                                        yield t
                        except Exception:
                            continue


# ==============================================================================
# OpenAI Provider (Architecture Ready — Not Activated in Phase 2A)
# ==============================================================================

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.base_url = "https://api.openai.com/v1"
        self.provider_name = "openai"

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise AIProviderMissingKeyError(self.provider_name)

        formatted_messages = [{"role": "system", "content": system_prompt}] + messages
        payload: Dict[str, Any] = {
            "model": model or "gpt-4o-mini",
            "messages": formatted_messages,
            "temperature": temperature,
        }
        if tools:
            payload["tools"] = tools

        async with httpx.AsyncClient(timeout=settings.AI_REQUEST_TIMEOUT_SECONDS) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload
            )
            if resp.status_code != 200:
                raise AIProviderAPIError(self.provider_name, resp.status_code, resp.text)
            data = resp.json()
            choice = data["choices"][0]["message"]
            return {
                "content": choice.get("content", ""),
                "provider": self.provider_name,
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
            raise AIProviderMissingKeyError(self.provider_name)

        formatted_messages = [{"role": "system", "content": system_prompt}] + messages
        payload = {
            "model": model or "gpt-4o-mini",
            "messages": formatted_messages,
            "temperature": temperature,
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=settings.AI_REQUEST_TIMEOUT_SECONDS) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload
            ) as resp:
                if resp.status_code != 200:
                    raw_err = await resp.aread()
                    raise AIProviderAPIError(self.provider_name, resp.status_code, raw_err.decode("utf-8", errors="ignore"))
                async for line in resp.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        try:
                            chunk = json.loads(line[6:])
                            delta = chunk["choices"][0]["delta"].get("content", "")
                            if delta:
                                yield delta
                        except Exception:
                            continue


# ==============================================================================
# Anthropic Provider (Architecture Ready — Not Activated in Phase 2A)
# ==============================================================================

class AnthropicProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.base_url = "https://api.anthropic.com/v1"
        self.provider_name = "anthropic"

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise AIProviderMissingKeyError(self.provider_name)

        claude_model = model or "claude-3-5-sonnet-20241022"
        formatted_messages = [{"role": m["role"], "content": m["content"]} for m in messages]

        payload = {
            "model": claude_model,
            "system": system_prompt,
            "messages": formatted_messages,
            "max_tokens": 4096,
            "temperature": temperature,
        }

        async with httpx.AsyncClient(timeout=settings.AI_REQUEST_TIMEOUT_SECONDS) as client:
            resp = await client.post(
                f"{self.base_url}/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json=payload
            )
            if resp.status_code != 200:
                raise AIProviderAPIError(self.provider_name, resp.status_code, resp.text)
            data = resp.json()
            content_blocks = data.get("content", [])
            text = "".join(b.get("text", "") for b in content_blocks if b.get("type") == "text")
            tokens = data.get("usage", {}).get("input_tokens", 0) + data.get("usage", {}).get("output_tokens", 0)
            return {
                "content": text,
                "provider": self.provider_name,
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


# ==============================================================================
# Mock Provider (Controlled Local Developer Simulator & Offline Testing)
# ==============================================================================

class MockProvider(BaseLLMProvider):
    """
    Intelligent Executive Fallback & Demo Engine.
    Strictly prohibited in production mode. Activated only when ALLOW_MOCK_FALLBACK=True
    in non-production environments.
    """
    def __init__(self):
        self.provider_name = "mock"

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

        for item in exec_results:
            domain = item.get("domain")
            action = item.get("action")

            if domain == "memory" and action == "stored":
                fact = item.get("fact", "your preference")
                content = (
                    f"### 🧠 Preference Stored (Simulation Mode)\n\n"
                    f"I have committed this to your executive memory bank:\n"
                    f"> **\"{fact}\"**\n\n"
                    f"I will respect this preference across future conversations."
                )
                return {"content": content, "provider": "mock", "model": "technopie-mock-v1", "tokens_used": 60, "tool_calls": []}

            elif domain == "memory" and action == "recalled":
                facts = item.get("facts", [])
                matched = [f for f in facts if "language" in f.lower() or "english" in f.lower() or "hindi" in f.lower()]
                pref_text = matched[0] if matched else "English"
                content = (
                    f"### 🧠 Recalled Preference (Simulation Mode)\n\n"
                    f"According to your personal memory bank, your preferred language is **{pref_text}**.\n\n"
                    f"I will ensure all future briefings and drafts are formatted accordingly."
                )
                return {"content": content, "provider": "mock", "model": "technopie-mock-v1", "tokens_used": 65, "tool_calls": []}

            elif domain == "tasks" and action == "created":
                title = item.get("task_title", "New Task")
                priority = item.get("priority", "medium").upper()
                due = item.get("due_date", "Tomorrow")
                content = (
                    f"### 📋 Task Created Successfully (Simulation Mode)\n\n"
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
                    f"### 📋 Priority & Task Management Report (Simulation Mode)\n\n"
                    f"I have audited your active task board and cross-referenced deadlines:\n\n"
                    f"{task_lines}\n\n"
                    f"**Recommendation:** Focus first on high and urgent deliverables before proceeding to lower-priority items."
                )
                return {"content": content, "provider": "mock", "model": "technopie-mock-v1", "tokens_used": 150, "tool_calls": []}

            elif domain == "research":
                content = (
                    "### 🔍 Competitive Intelligence: Top 5 AI Assistant SaaS Competitors (Simulation Mode)\n\n"
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

        # Fallback responses for general prompts
        content = (
            "Hello. I am your **Technopie AI Executive Assistant** (Running in Local Development Mock Mode).\n\n"
            "To connect real generative intelligence, set `GOOGLE_API_KEY` in your environment configuration.\n"
            "I am ready to assist with scheduling, email triage, task management, and document generation."
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


# ==============================================================================
# Model Router (Multi-Provider Abstraction & Policy Enforcement)
# ==============================================================================

class AIModelRouter:
    """
    Central router that dynamically selects the optimal model provider.
    Enforces strict production policies: NEVER silently cascades to MockProvider.
    """
    def __init__(self):
        self.openai = OpenAIProvider()
        self.gemini = GeminiProvider()
        self.anthropic = AnthropicProvider()
        self.mock = MockProvider()

    def get_provider(self, requested_provider: Optional[str] = None) -> BaseLLMProvider:
        prov = (requested_provider or settings.DEFAULT_AI_PROVIDER).lower()

        # 1. Explicit Mock Provider Request
        if prov == "mock":
            if settings.ENVIRONMENT == "production":
                raise AIProviderError(
                    message="Mock AI provider is strictly prohibited in production mode. Configure a real provider (Google Gemini).",
                    provider="mock",
                    status_code=403
                )
            return self.mock

        # 2. Google Gemini (Active Primary Foundation Provider in Phase 2A)
        if prov == "gemini":
            if settings.GOOGLE_API_KEY and settings.GOOGLE_API_KEY.strip():
                return self.gemini
            # Strict Policy: If key is missing, check if mock fallback is explicitly permitted
            if settings.ALLOW_MOCK_FALLBACK and settings.ENVIRONMENT != "production":
                logger.warning(
                    "GOOGLE_API_KEY is not configured; falling back to MockProvider because ALLOW_MOCK_FALLBACK is enabled in development."
                )
                return self.mock
            raise AIProviderMissingKeyError(
                provider="gemini",
                message="Google Gemini API key is missing. Set GOOGLE_API_KEY in your backend/.env file to enable real AI assistant capabilities."
            )

        # 3. OpenAI (Architecture Ready — Not Activated in Phase 2A)
        if prov == "openai":
            if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip():
                return self.openai
            raise AIProviderMissingKeyError(
                provider="openai",
                message="OpenAI provider is not active or OPENAI_API_KEY is missing."
            )

        # 4. Anthropic (Architecture Ready — Not Activated in Phase 2A)
        if prov == "anthropic":
            if settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY.strip():
                return self.anthropic
            raise AIProviderMissingKeyError(
                provider="anthropic",
                message="Anthropic provider is not active or ANTHROPIC_API_KEY is missing."
            )

        # 5. Unsupported Provider
        raise AIProviderError(
            message=f"Unsupported AI provider '{requested_provider}'. Supported providers: gemini, openai, anthropic, mock.",
            provider=prov,
            status_code=400
        )

model_router = AIModelRouter()
