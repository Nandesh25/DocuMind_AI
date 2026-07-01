from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import DocumentStatus
from app.schemas.tag_schema import TagResponse


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    uploaded_by: UUID | None
    title: str
    original_filename: str
    mime_type: str
    file_size_bytes: int
    status: DocumentStatus
    error_message: str | None
    page_count: int | None = None
    chunk_count: int | None = None
    word_count: int | None = None
    tags: list[TagResponse] = []
    created_at: datetime
    updated_at: datetime


class DocumentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    tag_ids: list[UUID] | None = None
