from abc import ABC, abstractmethod


class IEmbedder(ABC):
    """Port for turning text into dense vector embeddings.

    Services and the RAG retriever depend on this abstraction, not on any
    concrete model, keeping the embedding provider swappable (SOLID / DIP).
    """

    @property
    @abstractmethod
    def dimensions(self) -> int: ...

    @property
    @abstractmethod
    def model_name(self) -> str: ...

    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...

    @abstractmethod
    def embed_query(self, text: str) -> list[float]: ...
