from dataclasses import dataclass

from app.config.settings import settings
from app.rag.loaders import LoadedPage


@dataclass
class TextChunk:
    content: str
    index: int
    page_number: int | None


def chunk_pages(pages: list[LoadedPage]) -> list[TextChunk]:
    """Split loaded pages into overlapping character chunks."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks: list[TextChunk] = []
    index = 0
    for page in pages:
        for piece in splitter.split_text(page.text):
            cleaned = piece.strip()
            if not cleaned:
                continue
            chunks.append(
                TextChunk(content=cleaned, index=index, page_number=page.page_number)
            )
            index += 1
    return chunks


def estimate_tokens(text: str) -> int:
    """Rough token estimate (~4 chars/token) without external tokenizers."""
    return max(1, len(text) // 4)
