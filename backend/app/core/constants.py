from enum import StrEnum


class Role(StrEnum):
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"


class DocumentStatus(StrEnum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class SummaryType(StrEnum):
    SHORT = "short"
    DETAILED = "detailed"
    EXECUTIVE = "executive"


class QuizType(StrEnum):
    MCQ = "mcq"
    TRUE_FALSE = "true_false"
    SHORT = "short"


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


# Roles allowed to write (upload/edit/delete) within a workspace.
WRITE_ROLES = {Role.OWNER, Role.EDITOR}

# Canonical MIME types for the supported document formats.
MIME_PDF = "application/pdf"
MIME_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
MIME_TXT = "text/plain"
MIME_MARKDOWN = "text/markdown"

ALLOWED_MIME_TYPES = {MIME_PDF, MIME_DOCX, MIME_TXT, MIME_MARKDOWN}

# File extension -> canonical MIME. Used to reliably resolve the type when the
# browser sends a missing/generic content type (common for .md and .txt).
EXTENSION_MIME_MAP = {
    ".pdf": MIME_PDF,
    ".docx": MIME_DOCX,
    ".txt": MIME_TXT,
    ".md": MIME_MARKDOWN,
    ".markdown": MIME_MARKDOWN,
}
