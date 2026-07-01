from uuid import UUID

from pydantic import BaseModel, model_validator


class CompareRequest(BaseModel):
    document_a_id: UUID
    document_b_id: UUID

    @model_validator(mode="after")
    def _distinct_documents(self) -> "CompareRequest":
        if self.document_a_id == self.document_b_id:
            raise ValueError("Select two different documents to compare.")
        return self


class ComparedDocument(BaseModel):
    id: UUID
    title: str


class ComparisonResponse(BaseModel):
    document_a: ComparedDocument
    document_b: ComparedDocument
    similarity_score: float
    comparison: str
    model_name: str
