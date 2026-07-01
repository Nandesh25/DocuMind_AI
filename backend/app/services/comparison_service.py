import asyncio
from uuid import UUID

from app.ai.embeddings.minilm_embedder import get_embedder
from app.ai.llm.ollama_client import OllamaClient
from app.core.constants import DocumentStatus
from app.core.exceptions import NotFoundError, ValidationError
from app.models.document import Document
from app.rag.loaders import load_document
from app.rag.prompt_templates import build_comparison_prompt
from app.repositories.interfaces.i_document_repository import IDocumentRepository
from app.schemas.comparison_schema import (
    ComparedDocument,
    CompareRequest,
    ComparisonResponse,
)
from app.services.workspace_service import WorkspaceService

_MAX_COMPARE_CHARS = 8000


class ComparisonService:
    def __init__(
        self,
        document_repo: IDocumentRepository,
        workspace_service: WorkspaceService,
        llm_client: OllamaClient,
    ):
        self._documents = document_repo
        self._workspaces = workspace_service
        self._llm = llm_client

    async def compare(
        self, workspace_id: UUID, user_id: UUID, data: CompareRequest
    ) -> ComparisonResponse:
        await self._workspaces.require_member(workspace_id, user_id)

        doc_a = await self._require_indexed(data.document_a_id, workspace_id)
        doc_b = await self._require_indexed(data.document_b_id, workspace_id)

        # Extraction + embedding are blocking; run off the event loop.
        text_a = await asyncio.to_thread(self._extract, doc_a)
        text_b = await asyncio.to_thread(self._extract, doc_b)
        similarity = await asyncio.to_thread(self._similarity, text_a, text_b)

        comparison = await self._llm.generate(
            build_comparison_prompt(doc_a.title, text_a, doc_b.title, text_b)
        )

        return ComparisonResponse(
            document_a=ComparedDocument(id=doc_a.id, title=doc_a.title),
            document_b=ComparedDocument(id=doc_b.id, title=doc_b.title),
            similarity_score=similarity,
            comparison=comparison,
            model_name=self._llm.model_name,
        )

    async def _require_indexed(
        self, document_id: UUID, workspace_id: UUID
    ) -> Document:
        document = await self._documents.get_by_id(document_id)
        if not document or document.workspace_id != workspace_id:
            raise NotFoundError("Document not found in this workspace.")
        if document.status != DocumentStatus.INDEXED:
            raise ValidationError(
                f"Document '{document.title}' must be indexed before comparison."
            )
        return document

    def _extract(self, document: Document) -> str:
        pages = load_document(document.storage_path, document.mime_type)
        return "\n\n".join(page.text for page in pages)[:_MAX_COMPARE_CHARS]

    def _similarity(self, text_a: str, text_b: str) -> float:
        embedder = get_embedder()
        vec_a = embedder.embed_query(text_a)
        vec_b = embedder.embed_query(text_b)
        # Vectors are L2-normalized, so the dot product is cosine similarity.
        score = sum(a * b for a, b in zip(vec_a, vec_b, strict=False))
        return round(max(0.0, min(1.0, score)), 4)
