import logging
from app.llm.gemini_client import gemini_client

logger = logging.getLogger("agentos.rag")


async def embed_text(text: str) -> list[float] | None:
    """
    Returns a Gemini embedding vector, or None if the LLM call fails
    (e.g. no API key configured). Callers should fall back to Chroma's
    built-in embedding function by passing embeddings=None in that case.
    """
    try:
        return await gemini_client.embed(text)
    except Exception:  # noqa: BLE001
        logger.warning("Embedding call failed, falling back to Chroma default embedder", exc_info=True)
        return None
