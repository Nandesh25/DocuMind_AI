from uuid import UUID

from app.ai.embeddings.base import IEmbedder
from app.repositories.interfaces.i_vector_repository import IVectorRepository


def collection_name(workspace_id: UUID) -> str:
    """Deterministic, Chroma-safe collection name per workspace (tenant isolation)."""
    return f"ws_{workspace_id.hex}"


class Retriever:
    """Embeds a query and retrieves the most relevant chunks for a workspace."""

    def __init__(self, embedder: IEmbedder, vector_repo: IVectorRepository):
        self._embedder = embedder
        self._vectors = vector_repo

    def retrieve(
        self,
        workspace_id: UUID,
        query: str,
        top_k: int,
        document_ids: list[UUID] | None = None,
        min_score: float = 0.0,
    ) -> list[tuple[UUID, float, dict]]:
        """Return list of (chunk_id, score, metadata) above min_score."""
        query_vector = self._embedder.embed_query(query)
        where: dict | None = None
        if document_ids:
            where = {"document_id": {"$in": [str(d) for d in document_ids]}}

        raw = self._vectors.query(
            collection=collection_name(workspace_id),
            embedding=query_vector,
            top_k=top_k,
            where=where,
        )
        results: list[tuple[UUID, float, dict]] = []
        for vector_id, score, meta in raw:
            if score < min_score:
                continue
            chunk_id = meta.get("chunk_id", vector_id)
            try:
                results.append((UUID(str(chunk_id)), score, meta))
            except (ValueError, TypeError):
                continue
        return results
