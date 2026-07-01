"""RAG ingestion pipeline: extract text -> split into chunks.

This module exposes the first two stages of ingestion as a single cohesive,
testable unit. Persistence (storing chunks + vectors) is handled by the
IngestionService which consumes an ExtractionResult.
"""

from dataclasses import dataclass

from app.rag.chunker import TextChunk, chunk_pages
from app.rag.loaders import load_document


@dataclass
class ExtractionResult:
    chunks: list[TextChunk]
    page_count: int
    word_count: int

    @property
    def chunk_count(self) -> int:
        return len(self.chunks)


def extract_and_chunk(storage_path: str, mime_type: str) -> ExtractionResult:
    """Step 1 (extract) + Step 2 (split) of the pipeline."""
    pages = load_document(storage_path, mime_type)
    chunks = chunk_pages(pages)
    word_count = sum(len(chunk.content.split()) for chunk in chunks)
    return ExtractionResult(
        chunks=chunks,
        page_count=len(pages),
        word_count=word_count,
    )
