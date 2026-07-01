from functools import lru_cache

from app.config.settings import settings


@lru_cache
def get_chroma_client():
    """Return a ChromaDB client (singleton).

    Uses an HTTP client when CHROMA_HOST is configured (containerized service),
    otherwise falls back to an embedded persistent client on local disk.
    """
    import chromadb
    from chromadb.config import Settings as ChromaSettings

    common = ChromaSettings(anonymized_telemetry=False, allow_reset=False)

    if settings.CHROMA_HOST:
        return chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT,
            settings=common,
        )

    return chromadb.PersistentClient(path=settings.CHROMA_DIR, settings=common)
