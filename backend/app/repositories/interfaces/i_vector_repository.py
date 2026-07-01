from abc import ABC, abstractmethod


class IVectorRepository(ABC):
    """Abstraction over the vector store (ChromaDB)."""

    @abstractmethod
    def upsert(
        self,
        collection: str,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict],
    ) -> None: ...

    @abstractmethod
    def query(
        self,
        collection: str,
        embedding: list[float],
        top_k: int,
        where: dict | None = None,
    ) -> list[tuple[str, float, dict]]:
        """Return list of (vector_id, score, metadata) ordered by relevance."""

    @abstractmethod
    def delete(self, collection: str, ids: list[str]) -> None: ...
