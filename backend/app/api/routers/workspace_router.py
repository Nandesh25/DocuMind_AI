from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.dependencies import CurrentUser, WorkspaceServiceDep
from app.schemas.common import PageParams, PageResponse
from app.schemas.workspace_schema import (
    MemberAdd,
    MemberResponse,
    MemberUpdate,
    WorkspaceCreate,
    WorkspaceResponse,
    WorkspaceUpdate,
)

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.get("", response_model=PageResponse[WorkspaceResponse])
async def list_workspaces(
    current_user: CurrentUser,
    service: WorkspaceServiceDep,
    params: PageParams = Depends(),
) -> PageResponse[WorkspaceResponse]:
    items, total = await service.list_for_user(
        current_user.id, params.offset, params.size
    )
    return PageResponse(
        items=[WorkspaceResponse.model_validate(w) for w in items],
        total=total,
        page=params.page,
        size=params.size,
    )


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    data: WorkspaceCreate, current_user: CurrentUser, service: WorkspaceServiceDep
) -> WorkspaceResponse:
    workspace = await service.create(current_user.id, data)
    return WorkspaceResponse.model_validate(workspace)


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: UUID, current_user: CurrentUser, service: WorkspaceServiceDep
) -> WorkspaceResponse:
    workspace = await service.get(workspace_id, current_user.id)
    return WorkspaceResponse.model_validate(workspace)


@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: UUID,
    data: WorkspaceUpdate,
    current_user: CurrentUser,
    service: WorkspaceServiceDep,
) -> WorkspaceResponse:
    workspace = await service.update(workspace_id, current_user.id, data)
    return WorkspaceResponse.model_validate(workspace)


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace_id: UUID, current_user: CurrentUser, service: WorkspaceServiceDep
) -> None:
    await service.delete(workspace_id, current_user.id)
    return None


# --- Members ------------------------------------------------------------------
def _member_response(member, email: str, full_name: str) -> MemberResponse:
    return MemberResponse(
        user_id=member.user_id,
        email=email,
        full_name=full_name,
        role=member.role,
        joined_at=member.joined_at,
    )


@router.get("/{workspace_id}/members", response_model=list[MemberResponse])
async def list_members(
    workspace_id: UUID, current_user: CurrentUser, service: WorkspaceServiceDep
) -> list[MemberResponse]:
    members = await service.list_members(workspace_id, current_user.id)
    return [_member_response(m, email, name) for m, email, name in members]


@router.post(
    "/{workspace_id}/members",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_member(
    workspace_id: UUID,
    data: MemberAdd,
    current_user: CurrentUser,
    service: WorkspaceServiceDep,
) -> MemberResponse:
    member, email, name = await service.add_member(workspace_id, current_user.id, data)
    return _member_response(member, email, name)


@router.patch(
    "/{workspace_id}/members/{user_id}", response_model=MemberResponse
)
async def update_member(
    workspace_id: UUID,
    user_id: UUID,
    data: MemberUpdate,
    current_user: CurrentUser,
    service: WorkspaceServiceDep,
) -> MemberResponse:
    member, email, name = await service.update_member(
        workspace_id, current_user.id, user_id, data
    )
    return _member_response(member, email, name)


@router.delete(
    "/{workspace_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_member(
    workspace_id: UUID,
    user_id: UUID,
    current_user: CurrentUser,
    service: WorkspaceServiceDep,
) -> None:
    await service.remove_member(workspace_id, current_user.id, user_id)
    return None
