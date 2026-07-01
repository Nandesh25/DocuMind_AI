from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base_class import Base, UUIDMixin


class RevokedToken(UUIDMixin, Base):
    """Denylist of revoked refresh-token identifiers (jti).

    A refresh token is invalidated on logout or after rotation; its `jti` is
    stored here until the token would have expired anyway.
    """

    __tablename__ = "revoked_tokens"

    jti: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
