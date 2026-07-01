from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    CHAR,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import DocumentStatus
from app.database.base_class import Base, TimestampMixin, UUIDMixin
from app.models.tag import document_tags

if TYPE_CHECKING:
    from app.models.document_chunk import DocumentChunk
    from app.models.summary import Summary
    from app.models.tag import Tag
    from app.models.workspace import Workspace


class Document(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "documents"
    __table_args__ = (
        UniqueConstraint(
            "workspace_id", "checksum_sha256", name="uq_workspace_checksum"
        ),
    )

    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    uploaded_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(CHAR(64), nullable=False)
    status: Mapped[DocumentStatus] = mapped_column(
        String(20), nullable=False, default=DocumentStatus.UPLOADED, index=True
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Derived metadata populated during ingestion (extract -> split -> store).
    page_count: Mapped[int | None] = mapped_column(nullable=True)
    chunk_count: Mapped[int | None] = mapped_column(nullable=True)
    word_count: Mapped[int | None] = mapped_column(nullable=True)

    workspace: Mapped[Workspace] = relationship(back_populates="documents")
    chunks: Mapped[list[DocumentChunk]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )
    summaries: Mapped[list[Summary]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )
    tags: Mapped[list[Tag]] = relationship(
        secondary=document_tags, back_populates="documents"
    )
