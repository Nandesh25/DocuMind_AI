import asyncio
import json
import re
from uuid import UUID

from app.ai.llm.ollama_client import OllamaClient
from app.core.constants import DocumentStatus
from app.core.exceptions import NotFoundError, ValidationError
from app.models.document import Document
from app.rag.loaders import load_document
from app.rag.prompt_templates import build_flashcards_prompt
from app.repositories.interfaces.i_document_repository import IDocumentRepository
from app.schemas.flashcard_schema import (
    Flashcard,
    FlashcardRequest,
    FlashcardResponse,
)
from app.services.workspace_service import WorkspaceService

_MAX_FLASHCARD_CHARS = 10000
_JSON_ARRAY = re.compile(r"\[.*\]", re.DOTALL)


class FlashcardService:
    def __init__(
        self,
        document_repo: IDocumentRepository,
        workspace_service: WorkspaceService,
        llm_client: OllamaClient,
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
        cards = self._parse(raw)

        return FlashcardResponse(
            document_id=document.id,
            model_name=self._llm.model_name,
            cards=cards,
        )

    def _extract(self, document: Document) -> str:
        pages = load_document(document.storage_path, document.mime_type)
        return "\n\n".join(page.text for page in pages)[:_MAX_FLASHCARD_CHARS]

    def _parse(self, raw: str) -> list[Flashcard]:
        match = _JSON_ARRAY.search(raw)
        if not match:
            raise ValidationError(
                "The model did not return valid flashcards. Please try again."
            )
        try:
            items = json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise ValidationError(
                "The generated flashcards could not be parsed. Please try again."
            ) from exc

        cards: list[Flashcard] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            front = item.get("front")
            back = item.get("back")
            if not front or not back:
                continue
            cards.append(
                Flashcard(
                    front=str(front),
                    back=str(back),
                    hint=str(item["hint"]) if item.get("hint") else None,
                )
            )

        if not cards:
            raise ValidationError(
                "No flashcards could be generated. Please try again."
            )
        return cards
