from abc import ABC, abstractmethod
from uuid import UUID

from app.core.constants import Role
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember


class IWorkspaceRepository(ABC):
    @abstractmethod
    async def get_by_id(self, workspace_id: UUID) -> Workspace | None: ...

    @abstractmethod
    async def slug_exists(self, slug: str) -> bool: ...

    @abstractmethod
    async def add(self, workspace: Workspace) -> Workspace: ...

    @abstractmethod
    async def delete(self, workspace: Workspace) -> None: ...

    @abstractmethod
    async def list_for_user(
        self, user_id: UUID, offset: int, limit: int
    ) -> tuple[list[Workspace], int]: ...

    @abstractmethod
    async def get_member(
        self, workspace_id: UUID, user_id: UUID
    ) -> WorkspaceMember | None: ...

    @abstractmethod
    async def get_role(self, workspace_id: UUID, user_id: UUID) -> Role | None: ...

    @abstractmethod
    async def list_members(self, workspace_id: UUID) -> list[WorkspaceMember]: ...

    @abstractmethod
    async def add_member(self, member: WorkspaceMember) -> WorkspaceMember: ...

    @abstractmethod
    async def remove_member(self, member: WorkspaceMember) -> None: ...
