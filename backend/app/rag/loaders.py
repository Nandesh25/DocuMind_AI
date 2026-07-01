import re
from pathlib import Path

from app.core.exceptions import ValidationError

# Collapse 3+ blank lines and strip control characters that break embedding.
_MULTI_NEWLINE = re.compile(r"\n{3,}")
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


class LoadedPage:
    def __init__(self, text: str, page_number: int | None = None):
        self.text = text
        self.page_number = page_number


def _clean(text: str) -> str:
    """Normalize extracted text: drop control chars and excess whitespace."""
    text = _CONTROL_CHARS.sub(" ", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _MULTI_NEWLINE.sub("\n\n", text)
    return text.strip()


def load_document(path: str, mime_type: str) -> list[LoadedPage]:
    """Load a document into page-aware text segments based on its MIME type."""
    file_path = Path(path)
    if not file_path.exists():
        raise ValidationError("Stored file could not be found for extraction.")

    if mime_type == "application/pdf":
        return _load_pdf(file_path)
    if (
        mime_type
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ):
        return _load_docx(file_path)
    # text/plain and text/markdown
    return _load_text(file_path)


def _load_pdf(path: Path) -> list[LoadedPage]:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages: list[LoadedPage] = []
    for idx, page in enumerate(reader.pages, start=1):
        try:
            raw = page.extract_text() or ""
        except Exception:  # noqa: BLE001 - skip unreadable pages, keep going
            raw = ""
        text = _clean(raw)
        if text:
            pages.append(LoadedPage(text=text, page_number=idx))
    return pages


def _load_docx(path: Path) -> list[LoadedPage]:
    import docx

    document = docx.Document(str(path))
    parts = [p.text for p in document.paragraphs if p.text.strip()]
    text = _clean("\n".join(parts))
    return [LoadedPage(text=text, page_number=None)] if text else []


def _load_text(path: Path) -> list[LoadedPage]:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    text = _clean(raw)
    return [LoadedPage(text=text, page_number=None)] if text else []
