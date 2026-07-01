from app.core.constants import (
    MIME_DOCX,
    MIME_MARKDOWN,
    MIME_PDF,
    MIME_TXT,
)
from app.utils.file_utils import (
    compute_sha256,
    resolve_content_type,
    slugify,
    unique_slug,
)


def test_compute_sha256_known_value():
    # sha256("abc")
    assert (
        compute_sha256(b"abc")
        == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    )


def test_slugify():
    assert slugify("Hello World!") == "hello-world"
    assert slugify("  Legal & Finance  ") == "legal-finance"
    assert slugify("") == "workspace"


def test_unique_slug_prefix():
    slug = unique_slug("Legal Team")
    assert slug.startswith("legal-team-")
    assert unique_slug("X") != unique_slug("X")


def test_resolve_content_type_by_extension():
    assert resolve_content_type("a.pdf", None) == MIME_PDF
    assert resolve_content_type("a.docx", None) == MIME_DOCX
    assert resolve_content_type("notes.md", "application/octet-stream") == MIME_MARKDOWN
    assert resolve_content_type("x.txt", "") == MIME_TXT


def test_resolve_content_type_fallback_and_reject():
    # No extension but a valid provided MIME.
    assert resolve_content_type(None, MIME_PDF) == MIME_PDF
    # Unsupported type.
    assert resolve_content_type("a.exe", "application/x-msdownload") is None
