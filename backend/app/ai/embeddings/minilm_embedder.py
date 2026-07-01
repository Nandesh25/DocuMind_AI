from functools import lru_cache

from app.ai.embeddings.base import IEmbedder
from app.config.settings import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@lru_cache
def _get_model():
    """Lazily load the sentence-transformers embedding model (singleton)."""
    from sentence_transformers import SentenceTransformer

    logger.info("Loading embedding model: %s", settings.EMBEDDING_MODEL)
    model = SentenceTransformer(settings.EMBEDDING_MODEL)

    # Guard against a config/model dimension mismatch (vectors must line up
    # with what ChromaDB and embedding_metadata expect).
    actual_dim = model.get_sentence_embedding_dimension()
    if actual_dim != settings.EMBEDDING_DIMENSIONS:
        logger.warning(
            "Embedding dimension mismatch: model=%s reports %d but "
            "EMBEDDING_DIMENSIONS=%d. Using the model's value.",
            settings.EMBEDDING_MODEL,
            actual_dim,
            settings.EMBEDDING_DIMENSIONS,
        )
    return model


class Embedder(IEmbedder):
    """all-MiniLM-L6-v2 embedder producing L2-normalized 384-dim vectors."""

    @property
    def dimensions(self) -> int:
        return int(_get_model().get_sentence_embedding_dimension())

    @property
    def model_name(self) -> str:
        return settings.EMBEDDING_MODEL

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors = _get_model().encode(
            texts,
            batch_size=settings.EMBEDDING_BATCH_SIZE,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return vectors.tolist()

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]

    def warmup(self) -> None:
        """Force model load (e.g. at startup) to avoid first-request latency."""
        _get_model()


@lru_cache
def get_embedder() -> Embedder:
    return Embedder()

