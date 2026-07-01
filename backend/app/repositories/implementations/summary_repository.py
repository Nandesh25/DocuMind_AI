from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import SummaryType
from app.models.summary import Summary
from app.repositories.interfaces.i_summary_repository import ISummaryRepository


class SummaryRepository(ISummaryRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_document_and_type(
        self, document_id: UUID, summary_type: SummaryType
    ) -> Summary | None:
        result = await self._session.execute(
            select(Summary).where(
                Summary.document_id == document_id,
                Summary.summary_type == summary_type,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_document(self, document_id: UUID) -> list[Summary]:
        result = await self._session.execute(
            select(Summary)
            .where(Summary.document_id == document_id)
            .order_by(Summary.created_at.desc())
        )
        return list(result.scalars().all())

    async def add(self, summary: Summary) -> Summary:
        self._session.add(summary)
        await self._session.flush()
        await self._session.refresh(summary)
        return summary

    async def get_by_id(self, summary_id: UUID) -> Summary | None:
        return await self._session.get(Summary, summary_id)

    async def delete(self, summary: Summary) -> None:
        await self._session.delete(summary)
