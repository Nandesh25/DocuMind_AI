from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse

from app.core.dependencies import ChatServiceDep, CurrentUser
from app.schemas.chat_schema import (
    ChatCreate,
    ChatResponse,
    ChatUpdate,
    MessageCreate,
    MessageResponse,
)
from app.schemas.common import PageParams, PageResponse

router = APIRouter(tags=["Chats"])


@router.get(
    "/workspaces/{workspace_id}/chats", response_model=PageResponse[ChatResponse]
)
async def list_chats(
    workspace_id: UUID,
    current_user: CurrentUser,
    service: ChatServiceDep,
    params: PageParams = Depends(),
) -> PageResponse[ChatResponse]:
    items, total = await service.list(
        workspace_id, current_user.id, params.offset, params.size
    )
    return PageResponse(
        items=[ChatResponse.model_validate(c) for c in items],
        total=total,
        page=params.page,
        size=params.size,
    )


@router.post(
    "/workspaces/{workspace_id}/chats",
    response_model=ChatResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_chat(
    workspace_id: UUID,
    data: ChatCreate,
    current_user: CurrentUser,
    service: ChatServiceDep,
) -> ChatResponse:
    chat = await service.create(workspace_id, current_user.id, data)
    return ChatResponse.model_validate(chat)


@router.get("/chats/{chat_id}", response_model=ChatResponse)
async def get_chat(
    chat_id: UUID, current_user: CurrentUser, service: ChatServiceDep
) -> ChatResponse:
    chat = await service.get(chat_id, current_user.id)
    return ChatResponse.model_validate(chat)


@router.get(
    "/chats/{chat_id}/messages", response_model=PageResponse[MessageResponse]
)
async def list_messages(
    chat_id: UUID,
    current_user: CurrentUser,
    service: ChatServiceDep,
    params: PageParams = Depends(),
) -> PageResponse[MessageResponse]:
    items, total = await service.list_messages(
        chat_id, current_user.id, params.offset, params.size
    )
    return PageResponse(
        items=[MessageResponse.model_validate(m) for m in items],
        total=total,
        page=params.page,
        size=params.size,
    )


@router.post(
    "/chats/{chat_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def send_message(
    chat_id: UUID,
    data: MessageCreate,
    current_user: CurrentUser,
    service: ChatServiceDep,
) -> MessageResponse:
    message = await service.send_message(chat_id, current_user.id, data)
    return MessageResponse.model_validate(message)


@router.post("/chats/{chat_id}/messages/stream")
async def stream_message(
    chat_id: UUID,
    data: MessageCreate,
    current_user: CurrentUser,
    service: ChatServiceDep,
) -> StreamingResponse:
    generator = service.stream_message(chat_id, current_user.id, data)
    # Prime the generator so auth/validation errors become proper HTTP
    # responses before the streaming body (and 200 headers) begin.
    first_event = await generator.__anext__()

    async def body():
        yield first_event
        async for event in generator:
            yield event

    return StreamingResponse(
        body(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.patch("/chats/{chat_id}", response_model=ChatResponse)
async def update_chat(
    chat_id: UUID,
    data: ChatUpdate,
    current_user: CurrentUser,
    service: ChatServiceDep,
) -> ChatResponse:
    chat = await service.update(chat_id, current_user.id, data)
    return ChatResponse.model_validate(chat)


@router.delete("/chats/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
    chat_id: UUID, current_user: CurrentUser, service: ChatServiceDep
) -> None:
    await service.delete(chat_id, current_user.id)
    return None
