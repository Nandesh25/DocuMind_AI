from uuid import UUID

from pydantic import BaseModel, Field


class FlashcardRequest(BaseModel):
    num_cards: int = Field(default=10, ge=1, le=40)


class Flashcard(BaseModel):
    front: str
    back: str
    hint: str | None = None


class FlashcardResponse(BaseModel):
    document_id: UUID
    model_name: str
    cards: list[Flashcard]
