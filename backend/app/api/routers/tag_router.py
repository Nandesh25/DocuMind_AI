from uuid import UUID

from fastapi import APIRouter, status

from app.core.dependencies import CurrentUser, TagServiceDep
from app.schemas.tag_schema import TagCreate, TagResponse

router = APIRouter(tags=["Tags"])


@router.get("/workspaces/{workspace_id}/tags", response_model=list[TagResponse])
async def list_tags(
    workspace_id: UUID, current_user: CurrentUser, service: TagServiceDep
) -> list[TagResponse]:
    tags = await service.list(workspace_id, current_user.id)
    return [TagResponse.model_validate(t) for t in tags]


@router.post(
    "/workspaces/{workspace_id}/tags",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_tag(
    workspace_id: UUID,
    data: TagCreate,
    current_user: CurrentUser,
    service: TagServiceDep,
) -> TagResponse:
    tag = await service.create(workspace_id, current_user.id, data)
    return TagResponse.model_validate(tag)
