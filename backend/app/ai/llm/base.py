from abc import ABC, abstractmethod
from collections.abc import AsyncIterator


class ILLMClient(ABC):
    """Port for a chat LLM provider (Ollama, or any OpenAI-compatible API)."""

    @property
    @abstractmethod
    def model_name(self) -> str: ...

    @abstractmethod
    async def generate(self, prompt: str) -> str: ...

    @abstractmethod
    def astream(self, prompt: str) -> AsyncIterator[str]:
        """Yield the model's response token-by-token."""
        ...
