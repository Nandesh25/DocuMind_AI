from app.ai.llm.base import ILLMClient
from app.config.settings import settings
from app.core.exceptions import ServiceUnavailableError
from app.core.logging import get_logger

logger = get_logger(__name__)


class OpenAIClient(ILLMClient):
    """Adapter for any OpenAI-compatible chat endpoint (OpenAI, Groq, OpenRouter,
    Together, ...). Selected when LLM_PROVIDER=openai."""

    def __init__(self, model: str | None = None):
        self._model_name = model or settings.OPENAI_MODEL

    @property
    def model_name(self) -> str:
        return self._model_name

    def _build(self):
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=self._model_name,
            base_url=settings.OPENAI_BASE_URL,
            api_key=settings.OPENAI_API_KEY,
            temperature=settings.OLLAMA_TEMPERATURE,
            max_tokens=settings.OLLAMA_MAX_TOKENS,
        )

    async def generate(self, prompt: str) -> str:
        try:
            response = await self._build().ainvoke(prompt)
            return response.content if hasattr(response, "content") else str(response)
        except Exception as exc:  # noqa: BLE001
            logger.error("OpenAI-compatible generation failed: %s", exc)
            raise ServiceUnavailableError(
                "The language model is currently unavailable."
            ) from exc

    async def astream(self, prompt: str):
        try:
            async for chunk in self._build().astream(prompt):
                text = chunk.content if hasattr(chunk, "content") else str(chunk)
                if text:
                    yield text
        except Exception as exc:  # noqa: BLE001
            logger.error("OpenAI-compatible streaming failed: %s", exc)
            raise ServiceUnavailableError(
                "The language model is currently unavailable."
            ) from exc
