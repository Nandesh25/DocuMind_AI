from abc import ABC, abstractmethod
from uuid import UUID

from app.core.constants import SummaryType
from app.models.summary import Summary


class ISummaryRepository(ABC):
    @abstractmethod
    async def get_by_document_and_type(
        self, document_id: UUID, summary_type: SummaryType
    ) -> Summary | None: ...

    @abstractmethod
    async def list_by_document(self, document_id: UUID) -> list[Summary]: ...

    @abstractmethod
    async def add(self, summary: Summary) -> Summary: ...

    @abstractmethod
    async def get_by_id(self, summary_id: UUID) -> Summary | None: ...

    @abstractmethod
    async def delete(self, summary: Summary) -> None: ...
