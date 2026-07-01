from uuid import UUID

from fastapi import APIRouter

from app.core.dependencies import CurrentUser, QuizServiceDep
from app.schemas.quiz_schema import QuizRequest, QuizResponse

router = APIRouter(tags=["Quiz"])


@router.post("/documents/{document_id}/quiz", response_model=QuizResponse)
async def generate_quiz(
    document_id: UUID,
    data: QuizRequest,
    current_user: CurrentUser,
    service: QuizServiceDep,
) -> QuizResponse:
    """Generate a quiz (MCQ / True-False / Short answer) from a document."""
    return await service.generate(document_id, current_user.id, data)
