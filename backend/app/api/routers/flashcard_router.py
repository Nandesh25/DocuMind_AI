from uuid import UUID

from fastapi import APIRouter

from app.core.dependencies import CurrentUser, FlashcardServiceDep
from app.schemas.flashcard_schema import FlashcardRequest, FlashcardResponse

router = APIRouter(tags=["Flashcards"])


@router.post("/documents/{document_id}/flashcards", response_model=FlashcardResponse)
async def generate_flashcards(
    document_id: UUID,
    data: FlashcardRequest,
    current_user: CurrentUser,
    service: FlashcardServiceDep,
) -> FlashcardResponse:
    """Generate study flashcards (front/back) from a document."""
    return await service.generate(document_id, current_user.id, data)
