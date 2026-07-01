from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tag import Tag
from app.repositories.interfaces.i_tag_repository import ITagRepository


class TagRepository(ITagRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_ids(self, workspace_id: UUID, tag_ids: list[UUID]) -> list[Tag]:
        if not tag_ids:
            return []
        result = await self._session.execute(
            select(Tag).where(
                Tag.workspace_id == workspace_id, Tag.id.in_(tag_ids)
            )
        )
        return list(result.scalars().all())

    async def get_by_name(self, workspace_id: UUID, name: str) -> Tag | None:
        result = await self._session.execute(
            select(Tag).where(Tag.workspace_id == workspace_id, Tag.name == name)
        )
        return result.scalar_one_or_none()

    async def list_by_workspace(self, workspace_id: UUID) -> list[Tag]:
        result = await self._session.execute(
            select(Tag).where(Tag.workspace_id == workspace_id).order_by(Tag.name)
        )
        return list(result.scalars().all())

    async def add(self, tag: Tag) -> Tag:
        self._session.add(tag)
        await self._session.flush()
        await self._session.refresh(tag)
        return tag
