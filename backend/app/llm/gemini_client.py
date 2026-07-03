"""
Thin wrapper around the google-genai SDK so the rest of the codebase never
talks to the Gemini API directly. Centralizing this makes it trivial to:
  - swap models
  - add retries / timeouts
  - mock the LLM in tests (see tests/test_agents.py)
"""
import asyncio
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import settings

logger = logging.getLogger("agentos.llm")

_client = None


def _get_client():
    global _client
    if _client is None:
        from google import genai
        if not settings.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add it to backend/.env "
                "(copy from .env.example) to enable live LLM calls."
            )
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


class GeminiClient:
    """Synchronous-under-the-hood client exposed via async methods."""

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    def _generate_sync(self, system_prompt: str, user_prompt: str, temperature: float = 0.4) -> str:
        client = _get_client()
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=user_prompt,
            config={
                "system_instruction": system_prompt,
                "temperature": temperature,
            },
        )
        return response.text or ""

    async def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.4) -> str:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._generate_sync, system_prompt, user_prompt, temperature
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    def _embed_sync(self, text: str) -> list[float]:
        client = _get_client()
        result = client.models.embed_content(
            model=settings.GEMINI_EMBEDDING_MODEL,
            contents=text,
        )
        return result.embeddings[0].values

    async def embed(self, text: str) -> list[float]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._embed_sync, text)


gemini_client = GeminiClient()
