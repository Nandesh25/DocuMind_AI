from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.constants import SummaryType


class SummaryCreate(BaseModel):
    summary_type: SummaryType = SummaryType.SHORT


class SummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    summary_type: SummaryType
    content: str
    model_name: str
    created_at: datetime
