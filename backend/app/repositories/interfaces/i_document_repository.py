from abc import ABC, abstractmethod
from uuid import UUID

from app.core.constants import DocumentStatus
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.embedding_metadata import EmbeddingMetadata


class IDocumentRepository(ABC):
    @abstractmethod
    async def get_by_id(self, document_id: UUID) -> Document | None: ...

    @abstractmethod
    async def checksum_exists(self, workspace_id: UUID, checksum: str) -> bool: ...

    @abstractmethod
    async def add(self, document: Document) -> Document: ...

    @abstractmethod
    async def delete(self, document: Document) -> None: ...

    @abstractmethod
    async def list_by_workspace(
        self,
        workspace_id: UUID,
        offset: int,
        limit: int,
        status: DocumentStatus | None = None,
        query: str | None = None,
    ) -> tuple[list[Document], int]: ...

    @abstractmethod
    async def add_chunks(self, chunks: list[DocumentChunk]) -> None: ...

    @abstractmethod
    async def add_embedding(self, embedding: EmbeddingMetadata) -> None: ...

    @abstractmethod
    async def get_chunks_by_ids(self, chunk_ids: list[UUID]) -> list[DocumentChunk]: ...

    @abstractmethod
    async def count_indexed(self, workspace_id: UUID) -> int: ...

    @abstractmethod
    async def update(self, document: Document) -> Document: ...

    @abstractmethod
    async def get_chunk_ids_by_document(self, document_id: UUID) -> list[UUID]: ...

    @abstractmethod
    async def delete_chunks_by_document(self, document_id: UUID) -> None: ...
