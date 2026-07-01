from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Numeric, SmallInteger, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base_class import Base, UUIDMixin

if TYPE_CHECKING:
    from app.models.document_chunk import DocumentChunk
    from app.models.message import Message


class MessageSource(UUIDMixin, Base):
    __tablename__ = "message_sources"
    __table_args__ = (
        UniqueConstraint("message_id", "chunk_id", name="uq_message_chunk"),
    )

    message_id: Mapped[UUID] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True
    )
    chunk_id: Mapped[UUID] = mapped_column(
        ForeignKey("document_chunks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    relevance_score: Mapped[float | None] = mapped_column(Numeric(6, 5), nullable=True)
    rank: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    message: Mapped[Message] = relationship(back_populates="sources")
    chunk: Mapped[DocumentChunk] = relationship()
