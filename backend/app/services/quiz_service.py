import asyncio
import json
import re
from uuid import UUID

from app.ai.llm.ollama_client import OllamaClient
from app.core.constants import DocumentStatus
from app.core.exceptions import NotFoundError, ValidationError
from app.models.document import Document
from app.rag.loaders import load_document
from app.rag.prompt_templates import build_quiz_prompt
from app.repositories.interfaces.i_document_repository import IDocumentRepository
from app.schemas.quiz_schema import QuizQuestion, QuizRequest, QuizResponse
from app.services.workspace_service import WorkspaceService

_MAX_QUIZ_CHARS = 10000
_JSON_ARRAY = re.compile(r"\[.*\]", re.DOTALL)


class QuizService:
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
        self, document_id: UUID, user_id: UUID, data: QuizRequest
    ) -> QuizResponse:
        document = await self._documents.get_by_id(document_id)
        if not document:
            raise NotFoundError("Document not found.")
        await self._workspaces.require_member(document.workspace_id, user_id)
        if document.status != DocumentStatus.INDEXED:
            raise ValidationError("Document must be indexed before generating a quiz.")

        text = await asyncio.to_thread(self._extract, document)
        raw = await self._llm.generate(
            build_quiz_prompt(data.quiz_type.value, data.num_questions, text)
        )
        questions = self._parse(raw, data.quiz_type.value)

        return QuizResponse(
            document_id=document.id,
            quiz_type=data.quiz_type,
            model_name=self._llm.model_name,
            questions=questions,
        )

    def _extract(self, document: Document) -> str:
        pages = load_document(document.storage_path, document.mime_type)
        return "\n\n".join(page.text for page in pages)[:_MAX_QUIZ_CHARS]

    def _parse(self, raw: str, quiz_type: str) -> list[QuizQuestion]:
        match = _JSON_ARRAY.search(raw)
        if not match:
            raise ValidationError(
                "The model did not return a valid quiz. Please try again."
            )
        try:
            items = json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise ValidationError(
                "The generated quiz could not be parsed. Please try again."
            ) from exc

        questions: list[QuizQuestion] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            question = item.get("question")
            answer = item.get("answer")
            if not question or answer is None:
                continue

            options = item.get("options")
            if quiz_type == "true_false":
                options = ["True", "False"]
            elif not isinstance(options, list):
                options = None
            else:
                options = [str(o) for o in options]

            questions.append(
                QuizQuestion(
                    question=str(question),
                    options=options,
                    answer=str(answer),
                    explanation=(
                        str(item["explanation"])
                        if item.get("explanation")
                        else None
                    ),
                )
            )

        if not questions:
            raise ValidationError(
                "No quiz questions could be generated. Please try again."
            )
        return questions
