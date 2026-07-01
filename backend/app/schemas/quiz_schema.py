from uuid import UUID

from pydantic import BaseModel, Field

from app.core.constants import QuizType


class QuizRequest(BaseModel):
    quiz_type: QuizType = QuizType.MCQ
    num_questions: int = Field(default=5, ge=1, le=20)


class QuizQuestion(BaseModel):
    question: str
    options: list[str] | None = None
    answer: str
    explanation: str | None = None


class QuizResponse(BaseModel):
    document_id: UUID
    quiz_type: QuizType
    model_name: str
    questions: list[QuizQuestion]
