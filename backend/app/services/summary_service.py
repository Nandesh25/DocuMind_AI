from uuid import UUID

from app.ai.llm.base import ILLMClient
from app.core.constants import WRITE_ROLES, DocumentStatus
from app.core.exceptions import NotFoundError, ValidationError
from app.models.summary import Summary
from app.rag.loaders import load_document
from app.rag.prompt_templates import build_summary_prompt
from app.repositories.interfaces.i_document_repository import IDocumentRepository
from app.repositories.interfaces.i_summary_repository import ISummaryRepository
from app.schemas.summary_schema import SummaryCreate
from app.services.workspace_service import WorkspaceService

_MAX_SUMMARY_CHARS = 12000


class SummaryService:
    def __init__(
        self,
        summary_repo: ISummaryRepository,
        document_repo: IDocumentRepository,
        workspace_service: WorkspaceService,
        llm_client: ILLMClient,
    ):
        self._summaries = summary_repo
        self._documents = document_repo
        self._workspaces = workspace_service
        self._llm = llm_client

    async def generate(
        self, document_id: UUID, user_id: UUID, data: SummaryCreate
    ) -> tuple[Summary, bool]:
        """Return (summary, created). Cached summaries are returned as-is."""
        document = await self._documents.get_by_id(document_id)
        if not document:
            raise NotFoundError("Document not found.")
        await self._workspaces.require_member(document.workspace_id, user_id)

        if document.status != DocumentStatus.INDEXED:
            raise ValidationError("Document must be indexed before summarizing.")

        cached = await self._summaries.get_by_document_and_type(
            document_id, data.summary_type
        )
        if cached:
            return cached, False

        pages = load_document(document.storage_path, document.mime_type)
        text = "\n\n".join(p.text for p in pages)[:_MAX_SUMMARY_CHARS]
        content = await self._llm.generate(
            build_summary_prompt(data.summary_type.value, text)
        )

        summary = await self._summaries.add(
            Summary(
                document_id=document_id,
                generated_by=user_id,
                summary_type=data.summary_type,
                content=content,
                model_name=self._llm.model_name,
            )
        )
        return summary, True

    async def list(self, document_id: UUID, user_id: UUID) -> list[Summary]:
        document = await self._documents.get_by_id(document_id)
        if not document:
            raise NotFoundError("Document not found.")
        await self._workspaces.require_member(document.workspace_id, user_id)
        return await self._summaries.list_by_document(document_id)

    async def delete(self, summary_id: UUID, user_id: UUID) -> None:
        summary = await self._summaries.get_by_id(summary_id)
        if not summary:
            raise NotFoundError("Summary not found.")
        document = await self._documents.get_by_id(summary.document_id)
        if not document:
            raise NotFoundError("Summary not found.")
        await self._workspaces.require_role(document.workspace_id, user_id, WRITE_ROLES)
        await self._summaries.delete(summary)
