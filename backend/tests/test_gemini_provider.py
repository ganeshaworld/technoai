import os
import sys
import uuid
import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.config import settings
from backend.app.services.ai_providers import (
    GeminiProvider,
    MockProvider,
    AIModelRouter,
    AIProviderError,
    AIProviderMissingKeyError,
    AIProviderTimeoutError,
    AIProviderRateLimitError,
    AIProviderAPIError
)
from backend.app.agents.orchestrator import CentralAIBrain
from backend.app.db.session import AsyncSessionLocal
from backend.app.db.models import User
from backend.app.core.security import hash_password

# ------------------------------------------------------------------------------
# 1. Unit Tests: Missing API Key & Policy Enforcement
# ------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_gemini_missing_api_key_raises_error():
    """Verify that GeminiProvider raises AIProviderMissingKeyError when key is empty."""
    provider = GeminiProvider(api_key="")
    with pytest.raises(AIProviderMissingKeyError) as exc_info:
        await provider.generate_response(
            messages=[{"role": "user", "content": "Hello"}],
            system_prompt="Executive Assistant"
        )
    assert exc_info.value.provider == "gemini"
    assert exc_info.value.status_code == 503
    assert "GOOGLE_API_KEY is not configured" in str(exc_info.value)


def test_router_prohibits_silent_mock_fallback_when_disabled():
    """Verify router refuses silent mock fallback when ALLOW_MOCK_FALLBACK is False."""
    router = AIModelRouter()
    original_key = settings.GOOGLE_API_KEY
    original_fallback = settings.ALLOW_MOCK_FALLBACK
    try:
        settings.GOOGLE_API_KEY = ""
        settings.ALLOW_MOCK_FALLBACK = False

        with pytest.raises(AIProviderMissingKeyError) as exc_info:
            router.get_provider("gemini")
        assert "Google Gemini API key is missing" in str(exc_info.value)

        # Default provider should also raise rather than silently returning mock
        with pytest.raises(AIProviderMissingKeyError):
            router.get_provider(None)
    finally:
        settings.GOOGLE_API_KEY = original_key
        settings.ALLOW_MOCK_FALLBACK = original_fallback


def test_router_blocks_mock_in_production():
    """Verify MockProvider is rejected with 403 in production environment."""
    router = AIModelRouter()
    original_env = settings.ENVIRONMENT
    try:
        settings.ENVIRONMENT = "production"
        with pytest.raises(AIProviderError) as exc_info:
            router.get_provider("mock")
        assert exc_info.value.status_code == 403
        assert "strictly prohibited in production" in str(exc_info.value)
    finally:
        settings.ENVIRONMENT = original_env


def test_router_allows_mock_in_development_if_explicitly_configured():
    """Verify MockProvider is allowed only in development when ALLOW_MOCK_FALLBACK is True."""
    router = AIModelRouter()
    original_key = settings.GOOGLE_API_KEY
    original_env = settings.ENVIRONMENT
    original_fallback = settings.ALLOW_MOCK_FALLBACK
    try:
        settings.GOOGLE_API_KEY = ""
        settings.ENVIRONMENT = "development"
        settings.ALLOW_MOCK_FALLBACK = True

        provider = router.get_provider("gemini")
        assert isinstance(provider, MockProvider)
    finally:
        settings.GOOGLE_API_KEY = original_key
        settings.ENVIRONMENT = original_env
        settings.ALLOW_MOCK_FALLBACK = original_fallback


# ------------------------------------------------------------------------------
# 2. Unit Tests: Gemini HTTP Responses, Retries & Error Handling
# ------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_gemini_successful_response():
    """Verify GeminiProvider parses candidate text and token metadata correctly."""
    mock_payload = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": "Executive Briefing: Operations are optimal."}],
                    "role": "model"
                },
                "finishReason": "STOP"
            }
        ],
        "usageMetadata": {
            "promptTokenCount": 42,
            "candidatesTokenCount": 18,
            "totalTokenCount": 60
        }
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_payload

    provider = GeminiProvider(api_key="mock_test_key_ai_12345")

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        result = await provider.generate_response(
            messages=[{"role": "user", "content": "Status report"}],
            system_prompt="Executive Assistant",
            model="gemini-2.5-flash"
        )

    assert result["content"] == "Executive Briefing: Operations are optimal."
    assert result["provider"] == "gemini"
    assert result["model"] == "gemini-2.5-flash"
    assert result["tokens_used"] == 60
    assert result["prompt_tokens"] == 42
    assert result["completion_tokens"] == 18


@pytest.mark.asyncio
async def test_gemini_retries_transient_error_and_recovers():
    """Verify GeminiProvider retries on transient HTTP 429 and succeeds on next attempt."""
    resp_429 = MagicMock()
    resp_429.status_code = 429
    resp_429.text = '{"error": {"message": "Resource exhausted"}}'
    resp_429.json.return_value = {"error": {"message": "Resource exhausted"}}

    resp_200 = MagicMock()
    resp_200.status_code = 200
    resp_200.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "Recovered response"}]}}],
        "usageMetadata": {"totalTokenCount": 25}
    }

    provider = GeminiProvider(api_key="mock_test_key_ai_12345")

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = [resp_429, resp_200]
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            result = await provider.generate_response(
                messages=[{"role": "user", "content": "Retry test"}],
                system_prompt="Executive Assistant"
            )

    assert result["content"] == "Recovered response"
    assert mock_post.call_count == 2
    mock_sleep.assert_called_once()


@pytest.mark.asyncio
async def test_gemini_rate_limit_exhaustion():
    """Verify GeminiProvider raises AIProviderRateLimitError when retries are exhausted."""
    resp_429 = MagicMock()
    resp_429.status_code = 429
    resp_429.text = '{"error": {"message": "Rate limit exceeded"}}'
    resp_429.json.return_value = {"error": {"message": "Rate limit exceeded"}}

    provider = GeminiProvider(api_key="mock_test_key_ai_12345")

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = resp_429
        with patch("asyncio.sleep", new_callable=AsyncMock):
            with pytest.raises(AIProviderRateLimitError) as exc_info:
                await provider.generate_response(
                    messages=[{"role": "user", "content": "Exhaustion test"}],
                    system_prompt="Executive Assistant"
                )
    assert exc_info.value.status_code == 429
    assert exc_info.value.retryable is True


@pytest.mark.asyncio
async def test_gemini_timeout_exhaustion():
    """Verify GeminiProvider raises AIProviderTimeoutError on repeated timeouts."""
    provider = GeminiProvider(api_key="mock_test_key_ai_12345")

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.TimeoutException("Read timed out")
        with patch("asyncio.sleep", new_callable=AsyncMock):
            with pytest.raises(AIProviderTimeoutError) as exc_info:
                await provider.generate_response(
                    messages=[{"role": "user", "content": "Timeout test"}],
                    system_prompt="Executive Assistant"
                )
    assert exc_info.value.status_code == 504
    assert "did not respond within" in str(exc_info.value)


@pytest.mark.asyncio
async def test_gemini_non_retryable_client_error():
    """Verify GeminiProvider immediately raises AIProviderAPIError on HTTP 400 without retrying."""
    resp_400 = MagicMock()
    resp_400.status_code = 400
    resp_400.text = '{"error": {"message": "API key not valid"}}'
    resp_400.json.return_value = {"error": {"message": "API key not valid"}}

    provider = GeminiProvider(api_key="bad_key")

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = resp_400
        with pytest.raises(AIProviderAPIError) as exc_info:
            await provider.generate_response(
                messages=[{"role": "user", "content": "Client error test"}],
                system_prompt="Executive Assistant"
            )
    assert exc_info.value.status_code == 400
    assert "API key not valid" in str(exc_info.value)
    # Crucial: 400 should NOT retry
    assert mock_post.call_count == 1


# ------------------------------------------------------------------------------
# 3. Integration Tests: Orchestrator Graceful Handling
# ------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_orchestrator_handles_unconfigured_gemini_transparently():
    """Verify CentralAIBrain informs user of missing GOOGLE_API_KEY without crashing."""
    original_key = settings.GOOGLE_API_KEY
    original_fallback = settings.ALLOW_MOCK_FALLBACK
    try:
        settings.GOOGLE_API_KEY = ""
        settings.ALLOW_MOCK_FALLBACK = False

        async with AsyncSessionLocal() as db:
            # Create a test user for session
            unique_email = f"audit_gemini_{uuid.uuid4().hex[:8]}@technopie.ai"
            user = User(
                email=unique_email,
                hashed_password=hash_password("AuditTestPass123!")
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

            result = await CentralAIBrain.process_executive_request(
                db=db,
                user_id=user.id,
                user_name="Alexander",
                prompt="Remember that my preferred language is English",
                provider_name="gemini"
            )

        assert result["model_provider"] == "unconfigured"
        assert "AI Provider Configuration Required" in result["report"]
        assert "GOOGLE_API_KEY" in result["report"]
        assert result["intent"] == "memory_storage"
        # Tool execution still happened!
        assert len(result["execution_results"]) > 0
        assert result["execution_results"][0]["action"] == "stored"

    finally:
        settings.GOOGLE_API_KEY = original_key
        settings.ALLOW_MOCK_FALLBACK = original_fallback


# ------------------------------------------------------------------------------
# 4. Provider Status API Endpoint Tests
# ------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_provider_status_endpoint():
    """Verify GET /api/chat/provider-status returns provider configuration and health."""
    from backend.app.main import app
    from httpx import ASGITransport, AsyncClient

    transport = ASGITransport(app=app)
    status_email = f"status_user_{uuid.uuid4().hex[:8]}@technopie.ai"
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        await ac.post("/api/auth/register", json={
            "email": status_email,
            "password": "Password123!",
            "full_name": "Executive Status Tester",
            "profession": "Architect"
        })
        login_res = await ac.post("/api/auth/login", json={
            "email": status_email,
            "password": "Password123!"
        })
        token = login_res.json()["access_token"]

        res = await ac.get("/api/chat/provider-status", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        data = res.json()
        assert data["default_provider"] == "gemini"
        assert "gemini" in data["providers"]
        assert data["providers"]["gemini"]["active"] is True
        assert data["providers"]["gemini"]["fast_model"] == "gemini-2.5-flash"
        assert data["providers"]["openai"]["active"] is False
        assert data["providers"]["anthropic"]["active"] is False

# ------------------------------------------------------------------------------
# 5. Live API Test (Executed only if real GOOGLE_API_KEY is present in environment)
# ------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_live_gemini_inference():
    """
    Live end-to-end integration test against Google Generative Language API.
    Runs only when GOOGLE_API_KEY is provided in the environment.
    """
    api_key = settings.GOOGLE_API_KEY or os.environ.get("GOOGLE_API_KEY", "")
    if not api_key or api_key.startswith("your_") or api_key == "":
        pytest.skip("GOOGLE_API_KEY is not configured in environment. Skipping live Gemini test.")

    provider = GeminiProvider(api_key=api_key)
    res = await provider.generate_response(
        messages=[{"role": "user", "content": "Respond with the single word: CONFIRMED"}],
        system_prompt="You are Technopie AI.",
        model="gemini-2.5-flash"
    )

    assert res["provider"] == "gemini"
    assert res["model"] == "gemini-2.5-flash"
    assert res["tokens_used"] > 0
    assert "CONFIRMED" in res["content"].upper()
