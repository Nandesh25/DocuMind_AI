from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import MessageRole


class ChatCreate(BaseModel):
    title: str | None = Field(default=None, max_length=255)


class ChatUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=255)


class ChatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    user_id: UUID
    title: str | None
    created_at: datetime
    updated_at: datetime


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=4000)
    top_k: int = Field(default=5, ge=1, le=20)
    document_ids: list[UUID] | None = None


class MessageSourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_id: UUID
    chunk_id: UUID
    relevance_score: float | None
    rank: int | None


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    chat_id: UUID
    role: MessageRole
    content: str
    model_name: str | None
    latency_ms: int | None
    sources: list[MessageSourceResponse] = []
    created_at: datetime
