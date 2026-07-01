from abc import ABC, abstractmethod
from uuid import UUID

from app.models.chat import Chat
from app.models.message import Message


class IChatRepository(ABC):
    @abstractmethod
    async def get_by_id(self, chat_id: UUID) -> Chat | None: ...

    @abstractmethod
    async def add(self, chat: Chat) -> Chat: ...

    @abstractmethod
    async def delete(self, chat: Chat) -> None: ...

    @abstractmethod
    async def update(self, chat: Chat) -> Chat: ...

    @abstractmethod
    async def list_by_workspace(
        self, workspace_id: UUID, offset: int, limit: int
    ) -> tuple[list[Chat], int]: ...

    @abstractmethod
    async def search(
        self, workspace_id: UUID, query: str, offset: int, limit: int
    ) -> tuple[list[Chat], int]: ...

    @abstractmethod
    async def add_message(self, message: Message) -> Message: ...

    @abstractmethod
    async def list_messages(
        self, chat_id: UUID, offset: int, limit: int
    ) -> tuple[list[Message], int]: ...

    @abstractmethod
    async def recent_messages(self, chat_id: UUID, limit: int) -> list[Message]: ...
