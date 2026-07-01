from __future__ import annotations

from uuid import UUID

from fastapi import UploadFile

from app.config.settings import settings
from app.core.constants import (
    WRITE_ROLES,
    DocumentStatus,
)
from app.core.exceptions import (
    ConflictError,
    NotFoundError,
    ValidationError,
)
from app.models.document import Document
from app.rag.retriever import collection_name
from app.repositories.implementations.vector_repository import ChromaVectorRepository
from app.repositories.interfaces.i_document_repository import IDocumentRepository
from app.repositories.interfaces.i_tag_repository import ITagRepository
from app.schemas.document_schema import DocumentUpdate
from app.services.workspace_service import WorkspaceService
from app.utils.file_utils import (
    compute_sha256,
    delete_file,
    resolve_content_type,
    save_upload,
)


class DocumentService:
    def __init__(
        self,
        document_repo: IDocumentRepository,
        tag_repo: ITagRepository,
        workspace_service: WorkspaceService,
    ):
        self._documents = document_repo
        self._tags = tag_repo
        self._workspaces = workspace_service

    async def upload(
        self,
        workspace_id: UUID,
        user_id: UUID,
        file: UploadFile,
        title: str | None,
    ) -> Document:
        await self._workspaces.require_role(workspace_id, user_id, WRITE_ROLES)

        mime_type = resolve_content_type(file.filename, file.content_type)
        if mime_type is None:
            raise ValidationError(
                "Unsupported file type. Allowed formats: PDF, DOCX, TXT, Markdown."
            )

        data = await file.read()
        if len(data) == 0:
            raise ValidationError("Uploaded file is empty.")
        if len(data) > settings.max_upload_bytes:
            raise ValidationError(
                f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB}MB limit."
            )

        checksum = compute_sha256(data)
        if await self._documents.checksum_exists(workspace_id, checksum):
            raise ConflictError("This document already exists in the workspace.")

        storage_path = save_upload(str(workspace_id), file.filename or "document", data)
        document = Document(
            workspace_id=workspace_id,
            uploaded_by=user_id,
            title=title or (file.filename or "Untitled"),
            original_filename=file.filename or "document",
            storage_path=storage_path,
            mime_type=mime_type,
            file_size_bytes=len(data),
            checksum_sha256=checksum,
            status=DocumentStatus.UPLOADED,
        )
        return await self._documents.add(document)

    async def list(
        self,
        workspace_id: UUID,
        user_id: UUID,
        offset: int,
        limit: int,
        status: DocumentStatus | None,
        query: str | None,
    ) -> tuple[list[Document], int]:
        await self._workspaces.require_member(workspace_id, user_id)
        return await self._documents.list_by_workspace(
            workspace_id, offset, limit, status, query
        )

    async def get(self, document_id: UUID, user_id: UUID) -> Document:
        document = await self._documents.get_by_id(document_id)
        if not document:
            raise NotFoundError("Document not found.")
        await self._workspaces.require_member(document.workspace_id, user_id)
        return document

    async def update(
        self, document_id: UUID, user_id: UUID, data: DocumentUpdate
    ) -> Document:
        document = await self._documents.get_by_id(document_id)
        if not document:
            raise NotFoundError("Document not found.")
        await self._workspaces.require_role(document.workspace_id, user_id, WRITE_ROLES)

        if data.title is not None:
            document.title = data.title
        if data.tag_ids is not None:
            tags = await self._tags.get_by_ids(document.workspace_id, data.tag_ids)
            if len(tags) != len(set(data.tag_ids)):
                raise ValidationError("One or more tags do not belong to this workspace.")
            document.tags = tags
        return await self._documents.update(document)

    async def delete(self, document_id: UUID, user_id: UUID) -> None:
        document = await self._documents.get_by_id(document_id)
        if not document:
            raise NotFoundError("Document not found.")
        await self._workspaces.require_role(document.workspace_id, user_id, WRITE_ROLES)

        # Remove vectors from ChromaDB before cascading the relational rows.
        chunk_ids = [str(c.id) for c in document.chunks]
        if chunk_ids:
            try:
                ChromaVectorRepository().delete(
                    collection_name(document.workspace_id), chunk_ids
                )
            except Exception:  # noqa: BLE001 - best-effort vector cleanup
                pass

        storage_path = document.storage_path
        await self._documents.delete(document)
        delete_file(storage_path)

    async def reindex(self, document_id: UUID, user_id: UUID) -> Document:
        document = await self._documents.get_by_id(document_id)
        if not document:
            raise NotFoundError("Document not found.")
        await self._workspaces.require_role(document.workspace_id, user_id, WRITE_ROLES)
        if document.status == DocumentStatus.PROCESSING:
            raise ConflictError("Document is already being processed.")
        document.status = DocumentStatus.PROCESSING
        return await self._documents.update(document)
