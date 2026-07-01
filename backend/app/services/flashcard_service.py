import asyncio
from uuid import UUID

from app.ai.llm.base import ILLMClient
from app.core.constants import DocumentStatus
from app.core.exceptions import NotFoundError, ValidationError
from app.models.document import Document
from app.rag.loaders import load_document
from app.rag.output_parsers import parse_flashcards
from app.rag.prompt_templates import build_flashcards_prompt
from app.repositories.interfaces.i_document_repository import IDocumentRepository
from app.schemas.flashcard_schema import FlashcardRequest, FlashcardResponse
from app.services.workspace_service import WorkspaceService

_MAX_FLASHCARD_CHARS = 10000


class FlashcardService:
    def __init__(
        self,
        document_repo: IDocumentRepository,
        workspace_service: WorkspaceService,
        llm_client: ILLMClient,
    ):
        self._documents = document_repo
        self._workspaces = workspace_service
        self._llm = llm_client

    async def generate(
        self, document_id: UUID, user_id: UUID, data: FlashcardRequest
    ) -> FlashcardResponse:
        document = await self._documents.get_by_id(document_id)
        if not document:
            raise NotFoundError("Document not found.")
        await self._workspaces.require_member(document.workspace_id, user_id)
        if document.status != DocumentStatus.INDEXED:
            raise ValidationError(
                "Document must be indexed before generating flashcards."
            )

        text = await asyncio.to_thread(self._extract, document)
        raw = await self._llm.generate(
            build_flashcards_prompt(data.num_cards, text)
        )
        cards = parse_flashcards(raw)

        return FlashcardResponse(
            document_id=document.id,
            model_name=self._llm.model_name,
            cards=cards,
        )

    def _extract(self, document: Document) -> str:
        pages = load_document(document.storage_path, document.mime_type)
        return "\n\n".join(page.text for page in pages)[:_MAX_FLASHCARD_CHARS]
