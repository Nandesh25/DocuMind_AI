from functools import lru_cache

from app.ai.llm.base import ILLMClient
from app.config.settings import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@lru_cache
def get_llm_client() -> ILLMClient:
    """Return the configured chat LLM client (Ollama or OpenAI-compatible)."""
    if settings.LLM_PROVIDER.lower() == "openai":
        from app.ai.llm.openai_client import OpenAIClient

        return OpenAIClient()

    from app.ai.llm.ollama_client import OllamaClient

    return OllamaClient()
