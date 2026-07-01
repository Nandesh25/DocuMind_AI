from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base_class import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.chat import Chat
    from app.models.document import Document
    from app.models.tag import Tag
    from app.models.user import User
    from app.models.workspace_member import WorkspaceMember


class Workspace(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    owner: Mapped[User] = relationship(
        back_populates="owned_workspaces", foreign_keys=[owner_id]
    )
    members: Mapped[list[WorkspaceMember]] = relationship(
        back_populates="workspace", cascade="all, delete-orphan"
    )
    documents: Mapped[list[Document]] = relationship(
        back_populates="workspace", cascade="all, delete-orphan"
    )
    chats: Mapped[list[Chat]] = relationship(
        back_populates="workspace", cascade="all, delete-orphan"
    )
    tags: Mapped[list[Tag]] = relationship(
        back_populates="workspace", cascade="all, delete-orphan"
    )
