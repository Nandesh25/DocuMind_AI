from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.constants import DocumentStatus
from app.core.dependencies import (
    ChatServiceDep,
    CurrentUser,
    DocumentServiceDep,
    SearchServiceDep,
)
from app.schemas.chat_schema import ChatResponse
from app.schemas.common import PageParams, PageResponse
from app.schemas.document_schema import DocumentResponse
from app.schemas.search_schema import SearchRequest, SearchResponse

router = APIRouter(tags=["Search"])


@router.post("/workspaces/{workspace_id}/search", response_model=SearchResponse)
async def semantic_search(
    workspace_id: UUID,
    data: SearchRequest,
    current_user: CurrentUser,
    service: SearchServiceDep,
) -> SearchResponse:
    """Semantic (vector) search across the workspace's indexed documents."""
    return await service.semantic_search(workspace_id, current_user.id, data)


@router.get(
    "/workspaces/{workspace_id}/search/documents",
    response_model=PageResponse[DocumentResponse],
)
async def search_documents(
    workspace_id: UUID,
    current_user: CurrentUser,
    service: DocumentServiceDep,
    params: PageParams = Depends(),
    q: str | None = Query(default=None),
    status_filter: DocumentStatus | None = Query(default=None, alias="status"),
) -> PageResponse[DocumentResponse]:
    """Keyword/metadata search over document titles."""
    items, total = await service.list(
        workspace_id, current_user.id, params.offset, params.size, status_filter, q
    )
    return PageResponse(
        items=[DocumentResponse.model_validate(d) for d in items],
        total=total,
        page=params.page,
        size=params.size,
    )


@router.get(
    "/workspaces/{workspace_id}/search/chats",
    response_model=PageResponse[ChatResponse],
)
async def search_chats(
    workspace_id: UUID,
    current_user: CurrentUser,
    service: ChatServiceDep,
    q: str = Query(min_length=1),
    params: PageParams = Depends(),
) -> PageResponse[ChatResponse]:
    """Search chats by title or message content."""
    items, total = await service.search(
        workspace_id, current_user.id, q, params.offset, params.size
    )
    return PageResponse(
        items=[ChatResponse.model_validate(c) for c in items],
        total=total,
        page=params.page,
        size=params.size,
    )
