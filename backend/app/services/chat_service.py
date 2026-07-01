import json
import time
from collections.abc import AsyncIterator
from uuid import UUID

from app.core.constants import MessageRole
from app.core.exceptions import (
    ForbiddenError,
    NotFoundError,
    ServiceUnavailableError,
    ValidationError,
)
from app.models.chat import Chat
from app.models.message import Message
from app.models.message_source import MessageSource
from app.rag.rag_pipeline import RAGPipeline
from app.repositories.interfaces.i_chat_repository import IChatRepository
from app.repositories.interfaces.i_document_repository import IDocumentRepository
from app.schemas.chat_schema import ChatCreate, ChatUpdate, MessageCreate
from app.services.workspace_service import WorkspaceService

# Number of prior messages fed back into the prompt as conversation memory.
_HISTORY_LIMIT = 6


def _sse(event: str, data: dict) -> str:
    """Format a Server-Sent Events frame."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


class ChatService:
    def __init__(
        self,
        chat_repo: IChatRepository,
        document_repo: IDocumentRepository,
        workspace_service: WorkspaceService,
        rag_pipeline: RAGPipeline,
    ):
        self._chats = chat_repo
        self._documents = document_repo
        self._workspaces = workspace_service
        self._rag = rag_pipeline

    async def create(
        self, workspace_id: UUID, user_id: UUID, data: ChatCreate
    ) -> Chat:
        await self._workspaces.require_member(workspace_id, user_id)
        chat = Chat(workspace_id=workspace_id, user_id=user_id, title=data.title)
        return await self._chats.add(chat)

    async def list(
        self, workspace_id: UUID, user_id: UUID, offset: int, limit: int
    ) -> tuple[list[Chat], int]:
        await self._workspaces.require_member(workspace_id, user_id)
        return await self._chats.list_by_workspace(workspace_id, offset, limit)

    async def search(
        self, workspace_id: UUID, user_id: UUID, query: str, offset: int, limit: int
    ) -> tuple[list[Chat], int]:
        await self._workspaces.require_member(workspace_id, user_id)
        return await self._chats.search(workspace_id, query, offset, limit)

    async def get(self, chat_id: UUID, user_id: UUID) -> Chat:
        chat = await self._chats.get_by_id(chat_id)
        if not chat:
            raise NotFoundError("Chat not found.")
        await self._workspaces.require_member(chat.workspace_id, user_id)
        return chat

    async def list_messages(
        self, chat_id: UUID, user_id: UUID, offset: int, limit: int
    ) -> tuple[list[Message], int]:
        chat = await self.get(chat_id, user_id)
        return await self._chats.list_messages(chat.id, offset, limit)

    async def update(self, chat_id: UUID, user_id: UUID, data: ChatUpdate) -> Chat:
        chat = await self._chats.get_by_id(chat_id)
        if not chat:
            raise NotFoundError("Chat not found.")
        if chat.user_id != user_id:
            raise ForbiddenError("You can only edit your own chats.")
        chat.title = data.title
        return await self._chats.update(chat)

    async def delete(self, chat_id: UUID, user_id: UUID) -> None:
        chat = await self._chats.get_by_id(chat_id)
        if not chat:
            raise NotFoundError("Chat not found.")
        role = await self._workspaces.require_member(chat.workspace_id, user_id)
        from app.core.constants import Role

        if chat.user_id != user_id and role != Role.OWNER:
            raise ForbiddenError("You cannot delete this chat.")
        await self._chats.delete(chat)

    async def send_message(
        self, chat_id: UUID, user_id: UUID, data: MessageCreate
    ) -> Message:
        chat = await self._chats.get_by_id(chat_id)
        if not chat:
            raise NotFoundError("Chat not found.")
        await self._workspaces.require_member(chat.workspace_id, user_id)

        if await self._documents.count_indexed(chat.workspace_id) == 0:
            raise ValidationError(
                "This workspace has no indexed documents to answer from."
            )

        # Conversation history (prior turns) captured before the new question.
        history = await self._history(chat.id)

        # Persist the user's question.
        await self._chats.add_message(
            Message(chat_id=chat.id, role=MessageRole.USER, content=data.content)
        )

        # Run the RAG pipeline: retrieve -> assemble -> generate -> cite.
        result = await self._rag.answer(
            workspace_id=chat.workspace_id,
            question=data.content,
            top_k=data.top_k,
            document_ids=data.document_ids,
            chunk_resolver=self._documents.get_chunks_by_ids,
            history=history,
        )

        # Build citations up-front so no lazy relationship load happens later.
        sources = [
            MessageSource(
                chunk_id=src.chunk_id,
                document_id=src.document_id,
                relevance_score=src.score,
                rank=src.rank,
            )
            for src in result.sources
        ]

        assistant = Message(
            chat_id=chat.id,
            role=MessageRole.ASSISTANT,
            content=result.answer,
            model_name=result.model_name,
            latency_ms=result.latency_ms,
            sources=sources,
        )
        assistant = await self._chats.add_message(assistant)

        await self._chats.update(chat)  # touch updated_at
        return assistant

    async def stream_message(
        self, chat_id: UUID, user_id: UUID, data: MessageCreate
    ) -> AsyncIterator[str]:
        """Yield Server-Sent Events for a streamed RAG answer.

        Events: `sources` (citations), repeated `token` (text deltas), and a
        final `done` (persisted message id + latency), or `error`.
        """
        chat = await self._chats.get_by_id(chat_id)
        if not chat:
            raise NotFoundError("Chat not found.")
        await self._workspaces.require_member(chat.workspace_id, user_id)

        if await self._documents.count_indexed(chat.workspace_id) == 0:
            raise ValidationError(
                "This workspace has no indexed documents to answer from."
            )

        history = await self._history(chat.id)
        await self._chats.add_message(
            Message(chat_id=chat.id, role=MessageRole.USER, content=data.content)
        )

        prepared = await self._rag.prepare(
            workspace_id=chat.workspace_id,
            question=data.content,
            top_k=data.top_k,
            document_ids=data.document_ids,
            chunk_resolver=self._documents.get_chunks_by_ids,
            history=history,
        )

        source_payload = [
            {
                "document_id": str(s.document_id),
                "chunk_id": str(s.chunk_id),
                "relevance_score": s.score,
                "rank": s.rank,
            }
            for s in prepared.sources
        ]
        yield _sse("sources", {"sources": source_payload})

        started = time.perf_counter()
        buffer: list[str] = []
        try:
            async for token in self._rag.stream(prepared):
                buffer.append(token)
                yield _sse("token", {"content": token})
        except ServiceUnavailableError as exc:
            yield _sse("error", {"detail": exc.detail})
            return

        latency_ms = int((time.perf_counter() - started) * 1000)
        assistant = Message(
            chat_id=chat.id,
            role=MessageRole.ASSISTANT,
            content="".join(buffer),
            model_name=self._rag.model_name,
            latency_ms=latency_ms,
            sources=[
                MessageSource(
                    chunk_id=s.chunk_id,
                    document_id=s.document_id,
                    relevance_score=s.score,
                    rank=s.rank,
                )
                for s in prepared.sources
            ],
        )
        assistant = await self._chats.add_message(assistant)
        await self._chats.update(chat)
        yield _sse(
            "done", {"message_id": str(assistant.id), "latency_ms": latency_ms}
        )

    async def _history(self, chat_id: UUID) -> list[tuple[str, str]]:
        messages = await self._chats.recent_messages(chat_id, _HISTORY_LIMIT)
        return [(m.role.value, m.content) for m in messages]
