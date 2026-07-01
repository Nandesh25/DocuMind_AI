from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.settings import settings
from app.database.base_class import Base, UUIDMixin

if TYPE_CHECKING:
    from app.models.document_chunk import DocumentChunk


class EmbeddingMetadata(UUIDMixin, Base):
    __tablename__ = "embedding_metadata"

    chunk_id: Mapped[UUID] = mapped_column(
        ForeignKey("document_chunks.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    vector_id: Mapped[str] = mapped_column(String(100), nullable=False)
    collection_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    embedding_model: Mapped[str] = mapped_column(
        String(100), nullable=False, default=settings.EMBEDDING_MODEL
    )
    dimensions: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=settings.EMBEDDING_DIMENSIONS
    )
    indexed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    chunk: Mapped[DocumentChunk] = relationship(back_populates="embedding")
