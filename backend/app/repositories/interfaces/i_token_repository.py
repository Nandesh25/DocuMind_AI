from abc import ABC, abstractmethod
from datetime import datetime


class ITokenRepository(ABC):
    @abstractmethod
    async def is_revoked(self, jti: str) -> bool: ...

    @abstractmethod
    async def revoke(self, jti: str, expires_at: datetime) -> None: ...
