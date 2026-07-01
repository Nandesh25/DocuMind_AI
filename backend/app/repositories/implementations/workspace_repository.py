from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import Role
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember
from app.repositories.interfaces.i_workspace_repository import IWorkspaceRepository


class WorkspaceRepository(IWorkspaceRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, workspace_id: UUID) -> Workspace | None:
        return await self._session.get(Workspace, workspace_id)

    async def slug_exists(self, slug: str) -> bool:
        result = await self._session.execute(
            select(Workspace.id).where(Workspace.slug == slug)
        )
        return result.first() is not None

    async def add(self, workspace: Workspace) -> Workspace:
        self._session.add(workspace)
        await self._session.flush()
        await self._session.refresh(workspace)
        return workspace

    async def delete(self, workspace: Workspace) -> None:
        await self._session.delete(workspace)

    async def list_for_user(
        self, user_id: UUID, offset: int, limit: int
    ) -> tuple[list[Workspace], int]:
        base = (
            select(Workspace)
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
            .where(WorkspaceMember.user_id == user_id)
        )
        total = await self._session.scalar(
            select(func.count()).select_from(base.subquery())
        )
        result = await self._session.execute(
            base.order_by(Workspace.created_at.desc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all()), total or 0

    async def get_member(
        self, workspace_id: UUID, user_id: UUID
    ) -> WorkspaceMember | None:
        result = await self._session.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_role(self, workspace_id: UUID, user_id: UUID) -> Role | None:
        member = await self.get_member(workspace_id, user_id)
        return member.role if member else None

    async def list_members(self, workspace_id: UUID) -> list[WorkspaceMember]:
        result = await self._session.execute(
            select(WorkspaceMember)
            .where(WorkspaceMember.workspace_id == workspace_id)
            .order_by(WorkspaceMember.joined_at)
        )
        return list(result.scalars().all())

    async def add_member(self, member: WorkspaceMember) -> WorkspaceMember:
        self._session.add(member)
        await self._session.flush()
        await self._session.refresh(member)
        return member

    async def remove_member(self, member: WorkspaceMember) -> None:
        await self._session.delete(member)
