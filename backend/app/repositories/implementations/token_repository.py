from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.revoked_token import RevokedToken
from app.repositories.interfaces.i_token_repository import ITokenRepository


class TokenRepository(ITokenRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def is_revoked(self, jti: str) -> bool:
        result = await self._session.execute(
            select(RevokedToken.id).where(RevokedToken.jti == jti)
        )
        return result.first() is not None

    async def revoke(self, jti: str, expires_at: datetime) -> None:
        # Ignore duplicate revocations (idempotent).
        if await self.is_revoked(jti):
            return
        self._session.add(RevokedToken(jti=jti, expires_at=expires_at))
        await self._session.flush()
