from app.ai.vectorstore.chroma_client import get_chroma_client
from app.core.exceptions import ServiceUnavailableError
from app.core.logging import get_logger
from app.repositories.interfaces.i_vector_repository import IVectorRepository

logger = get_logger(__name__)


class ChromaVectorRepository(IVectorRepository):
    """ChromaDB-backed implementation of the vector store abstraction."""

    def __init__(self):
        try:
            self._client = get_chroma_client()
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to connect to ChromaDB: %s", exc)
            raise ServiceUnavailableError(
                "The vector store is currently unavailable."
            ) from exc

    def _collection(self, name: str):
        return self._client.get_or_create_collection(
            name=name, metadata={"hnsw:space": "cosine"}
        )

    def upsert(
        self,
        collection: str,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict],
    ) -> None:
        try:
            self._collection(collection).upsert(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("ChromaDB upsert failed: %s", exc)
            raise ServiceUnavailableError(
                "Failed to store embeddings in the vector store."
            ) from exc

    def query(
        self,
        collection: str,
        embedding: list[float],
        top_k: int,
        where: dict | None = None,
    ) -> list[tuple[str, float, dict]]:
        try:
            result = self._collection(collection).query(
                query_embeddings=[embedding],
                n_results=top_k,
                where=where,
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("ChromaDB query failed: %s", exc)
            raise ServiceUnavailableError(
                "The vector store is currently unavailable."
            ) from exc

        ids = result.get("ids", [[]])[0]
        distances = result.get("distances", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        out: list[tuple[str, float, dict]] = []
        for vid, dist, meta in zip(ids, distances, metadatas, strict=False):
            # cosine distance -> similarity score in [0, 1]
            score = max(0.0, 1.0 - float(dist))
            out.append((vid, score, meta or {}))
        return out

    def delete(self, collection: str, ids: list[str]) -> None:
        if not ids:
            return
        try:
            self._collection(collection).delete(ids=ids)
        except Exception as exc:  # noqa: BLE001
            logger.error("ChromaDB delete failed: %s", exc)
            raise ServiceUnavailableError(
                "Failed to remove embeddings from the vector store."
            ) from exc
