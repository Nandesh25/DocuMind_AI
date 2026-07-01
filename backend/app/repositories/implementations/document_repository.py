from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.constants import DocumentStatus
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.embedding_metadata import EmbeddingMetadata
from app.repositories.interfaces.i_document_repository import IDocumentRepository


class DocumentRepository(IDocumentRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, document_id: UUID) -> Document | None:
        result = await self._session.execute(
            select(Document)
            .where(Document.id == document_id)
            .options(selectinload(Document.tags))
        )
        return result.scalar_one_or_none()

    async def checksum_exists(self, workspace_id: UUID, checksum: str) -> bool:
        result = await self._session.execute(
            select(Document.id).where(
                Document.workspace_id == workspace_id,
                Document.checksum_sha256 == checksum,
            )
        )
        return result.first() is not None

    async def add(self, document: Document) -> Document:
        self._session.add(document)
        await self._session.flush()
        # Refresh only server-generated timestamps so the `tags` relationship
        # (empty for a new document) is not expired into an async lazy load.
        await self._session.refresh(
            document, attribute_names=["created_at", "updated_at"]
        )
        return document

    async def delete(self, document: Document) -> None:
        await self._session.delete(document)

    async def list_by_workspace(
        self,
        workspace_id: UUID,
        offset: int,
        limit: int,
        status: DocumentStatus | None = None,
        query: str | None = None,
    ) -> tuple[list[Document], int]:
        conditions = [Document.workspace_id == workspace_id]
        if status is not None:
            conditions.append(Document.status == status)
        if query:
            conditions.append(Document.title.ilike(f"%{query}%"))

        base = select(Document).where(*conditions)
        total = await self._session.scalar(
            select(func.count()).select_from(base.subquery())
        )
        result = await self._session.execute(
            base.options(selectinload(Document.tags))
            .order_by(Document.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all()), total or 0

    async def add_chunks(self, chunks: list[DocumentChunk]) -> None:
        self._session.add_all(chunks)
        await self._session.flush()

    async def add_embedding(self, embedding: EmbeddingMetadata) -> None:
        self._session.add(embedding)
        await self._session.flush()

    async def get_chunks_by_ids(self, chunk_ids: list[UUID]) -> list[DocumentChunk]:
        if not chunk_ids:
            return []
        result = await self._session.execute(
            select(DocumentChunk).where(DocumentChunk.id.in_(chunk_ids))
        )
        return list(result.scalars().all())

    async def count_indexed(self, workspace_id: UUID) -> int:
        return await self._session.scalar(
            select(func.count(Document.id)).where(
                Document.workspace_id == workspace_id,
                Document.status == DocumentStatus.INDEXED,
            )
        ) or 0

    async def update(self, document: Document) -> Document:
        await self._session.flush()
        await self._session.refresh(
            document, attribute_names=["created_at", "updated_at"]
        )
        return document

    async def get_chunk_ids_by_document(self, document_id: UUID) -> list[UUID]:
        result = await self._session.execute(
            select(DocumentChunk.id).where(DocumentChunk.document_id == document_id)
        )
        return list(result.scalars().all())

    async def delete_chunks_by_document(self, document_id: UUID) -> None:
        from sqlalchemy import delete as sa_delete

        await self._session.execute(
            sa_delete(DocumentChunk).where(DocumentChunk.document_id == document_id)
        )
        await self._session.flush()
