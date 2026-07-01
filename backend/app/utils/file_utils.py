import hashlib
import re
import unicodedata
import uuid
from pathlib import Path

from app.config.settings import settings
from app.core.constants import ALLOWED_MIME_TYPES, EXTENSION_MIME_MAP


def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def resolve_content_type(filename: str | None, provided_mime: str | None) -> str | None:
    """Resolve the canonical MIME type for a supported document.

    Prefers the file extension (reliable) and falls back to the browser-provided
    MIME type. Returns None if the format is not supported.
    """
    if filename:
        ext = Path(filename).suffix.lower()
        mapped = EXTENSION_MIME_MAP.get(ext)
        if mapped:
            return mapped
    if provided_mime and provided_mime in ALLOWED_MIME_TYPES:
        return provided_mime
    return None


def save_upload(workspace_id: str, filename: str, data: bytes) -> str:
    """Persist raw bytes under the workspace storage dir; return relative path."""
    base = Path(settings.STORAGE_DIR) / str(workspace_id)
    base.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid.uuid4().hex}_{Path(filename).name}"
    target = base / safe_name
    target.write_bytes(data)
    return str(target)


def delete_file(path: str) -> None:
    try:
        Path(path).unlink(missing_ok=True)
    except OSError:
        pass


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value or "workspace"


def unique_slug(value: str) -> str:
    return f"{slugify(value)}-{uuid.uuid4().hex[:6]}"
