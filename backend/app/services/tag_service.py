from __future__ import annotations

from uuid import UUID

from app.core.constants import WRITE_ROLES
from app.core.exceptions import ConflictError
from app.models.tag import Tag
from app.repositories.interfaces.i_tag_repository import ITagRepository
from app.schemas.tag_schema import TagCreate
from app.services.workspace_service import WorkspaceService


class TagService:
    def __init__(
        self,
        tag_repo: ITagRepository,
        workspace_service: WorkspaceService,
    ):
        self._tags = tag_repo
        self._workspaces = workspace_service

    async def list(self, workspace_id: UUID, user_id: UUID) -> list[Tag]:
        await self._workspaces.require_member(workspace_id, user_id)
        return await self._tags.list_by_workspace(workspace_id)

    async def create(
        self, workspace_id: UUID, user_id: UUID, data: TagCreate
    ) -> Tag:
        await self._workspaces.require_role(workspace_id, user_id, WRITE_ROLES)
        if await self._tags.get_by_name(workspace_id, data.name):
            raise ConflictError("A tag with this name already exists.")
        return await self._tags.add(
            Tag(workspace_id=workspace_id, name=data.name, color=data.color)
        )
