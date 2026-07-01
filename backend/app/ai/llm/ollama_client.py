from app.config.settings import settings
from app.core.exceptions import ServiceUnavailableError
from app.core.logging import get_logger

logger = get_logger(__name__)


class OllamaClient:
    """Adapter around a locally hosted Ollama chat model via LangChain."""

    def __init__(self, model: str | None = None):
        self._model_name = model or settings.OLLAMA_MODEL

    @property
    def model_name(self) -> str:
        return self._model_name

    def _build(self):
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=self._model_name,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=settings.OLLAMA_TEMPERATURE,
            num_ctx=settings.OLLAMA_NUM_CTX,
            num_predict=settings.OLLAMA_MAX_TOKENS,
        )

    async def generate(self, prompt: str) -> str:
        try:
            llm = self._build()
            response = await llm.ainvoke(prompt)
            return response.content if hasattr(response, "content") else str(response)
        except Exception as exc:  # noqa: BLE001 - surface as service outage
            logger.error("Ollama generation failed: %s", exc)
            raise ServiceUnavailableError(
                "The language model is currently unavailable."
            ) from exc

    async def astream(self, prompt: str):
        """Yield the model's response token-by-token."""
        try:
            llm = self._build()
            async for chunk in llm.astream(prompt):
                text = chunk.content if hasattr(chunk, "content") else str(chunk)
                if text:
                    yield text
        except Exception as exc:  # noqa: BLE001 - surface as service outage
            logger.error("Ollama streaming failed: %s", exc)
            raise ServiceUnavailableError(
                "The language model is currently unavailable."
            ) from exc


def get_llm_client() -> OllamaClient:
    return OllamaClient()
