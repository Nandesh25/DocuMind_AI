from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.chat import Chat
from app.models.message import Message
from app.repositories.interfaces.i_chat_repository import IChatRepository


class ChatRepository(IChatRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, chat_id: UUID) -> Chat | None:
        return await self._session.get(Chat, chat_id)

    async def add(self, chat: Chat) -> Chat:
        self._session.add(chat)
        await self._session.flush()
        await self._session.refresh(chat)
        return chat

    async def delete(self, chat: Chat) -> None:
        await self._session.delete(chat)

    async def update(self, chat: Chat) -> Chat:
        await self._session.flush()
        await self._session.refresh(chat)
        return chat

    async def list_by_workspace(
        self, workspace_id: UUID, offset: int, limit: int
    ) -> tuple[list[Chat], int]:
        base = select(Chat).where(Chat.workspace_id == workspace_id)
        total = await self._session.scalar(
            select(func.count()).select_from(base.subquery())
        )
        result = await self._session.execute(
            base.order_by(Chat.updated_at.desc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all()), total or 0

    async def search(
        self, workspace_id: UUID, query: str, offset: int, limit: int
    ) -> tuple[list[Chat], int]:
        pattern = f"%{query}%"
        matching_chat_ids = (
            select(Message.chat_id).where(Message.content.ilike(pattern)).subquery()
        )
        base = (
            select(Chat)
            .where(
                Chat.workspace_id == workspace_id,
                or_(
                    Chat.title.ilike(pattern),
                    Chat.id.in_(select(matching_chat_ids.c.chat_id)),
                ),
            )
        )
        total = await self._session.scalar(
            select(func.count()).select_from(base.subquery())
        )
        result = await self._session.execute(
            base.order_by(Chat.updated_at.desc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all()), total or 0

    async def add_message(self, message: Message) -> Message:
        self._session.add(message)
        await self._session.flush()
        # Refresh only server-generated timestamps to avoid expiring the
        # in-memory `sources` collection (which would trigger a lazy load).
        await self._session.refresh(message, attribute_names=["created_at", "updated_at"])
        return message

    async def list_messages(
        self, chat_id: UUID, offset: int, limit: int
    ) -> tuple[list[Message], int]:
        base = select(Message).where(Message.chat_id == chat_id)
        total = await self._session.scalar(
            select(func.count()).select_from(base.subquery())
        )
        result = await self._session.execute(
            base.options(selectinload(Message.sources))
            .order_by(Message.created_at)
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all()), total or 0

    async def recent_messages(self, chat_id: UUID, limit: int) -> list[Message]:
        result = await self._session.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        return list(reversed(result.scalars().all()))
