from abc import ABC, abstractmethod
from uuid import UUID

from app.models.tag import Tag


class ITagRepository(ABC):
    @abstractmethod
    async def get_by_ids(self, workspace_id: UUID, tag_ids: list[UUID]) -> list[Tag]: ...

    @abstractmethod
    async def get_by_name(self, workspace_id: UUID, name: str) -> Tag | None: ...

    @abstractmethod
    async def list_by_workspace(self, workspace_id: UUID) -> list[Tag]: ...

    @abstractmethod
    async def add(self, tag: Tag) -> Tag: ...
