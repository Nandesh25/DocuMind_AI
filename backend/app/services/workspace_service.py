from uuid import UUID

from app.core.constants import WRITE_ROLES, Role
from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember
from app.repositories.interfaces.i_user_repository import IUserRepository
from app.repositories.interfaces.i_workspace_repository import IWorkspaceRepository
from app.schemas.workspace_schema import (
    MemberAdd,
    MemberUpdate,
    WorkspaceCreate,
    WorkspaceUpdate,
)
from app.utils.file_utils import unique_slug


class WorkspaceService:
    def __init__(
        self,
        workspace_repo: IWorkspaceRepository,
        user_repo: IUserRepository,
    ):
        self._workspaces = workspace_repo
        self._users = user_repo

    # --- authorization helpers -------------------------------------------------
    async def require_role(
        self, workspace_id: UUID, user_id: UUID, allowed: set[Role]
    ) -> Role:
        role = await self._workspaces.get_role(workspace_id, user_id)
        if role is None:
            # Hide existence from non-members.
            raise NotFoundError("Workspace not found.")
        if role not in allowed:
            raise ForbiddenError("You do not have permission for this action.")
        return role

    async def require_member(self, workspace_id: UUID, user_id: UUID) -> Role:
        return await self.require_role(
            workspace_id, user_id, {Role.OWNER, Role.EDITOR, Role.VIEWER}
        )

    # --- workspace CRUD --------------------------------------------------------
    async def create(self, owner_id: UUID, data: WorkspaceCreate) -> Workspace:
        workspace = Workspace(
            name=data.name,
            description=data.description,
            slug=unique_slug(data.name),
            owner_id=owner_id,
        )
        workspace = await self._workspaces.add(workspace)
        await self._workspaces.add_member(
            WorkspaceMember(
                workspace_id=workspace.id, user_id=owner_id, role=Role.OWNER
            )
        )
        return workspace

    async def list_for_user(
        self, user_id: UUID, offset: int, limit: int
    ) -> tuple[list[Workspace], int]:
        return await self._workspaces.list_for_user(user_id, offset, limit)

    async def get(self, workspace_id: UUID, user_id: UUID) -> Workspace:
        await self.require_member(workspace_id, user_id)
        workspace = await self._workspaces.get_by_id(workspace_id)
        if not workspace:
            raise NotFoundError("Workspace not found.")
        return workspace

    async def update(
        self, workspace_id: UUID, user_id: UUID, data: WorkspaceUpdate
    ) -> Workspace:
        await self.require_role(workspace_id, user_id, WRITE_ROLES)
        workspace = await self._workspaces.get_by_id(workspace_id)
        if not workspace:
            raise NotFoundError("Workspace not found.")
        if data.name is not None:
            workspace.name = data.name
        if data.description is not None:
            workspace.description = data.description
        return await self._workspaces.add(workspace)

    async def delete(self, workspace_id: UUID, user_id: UUID) -> None:
        await self.require_role(workspace_id, user_id, {Role.OWNER})
        workspace = await self._workspaces.get_by_id(workspace_id)
        if not workspace:
            raise NotFoundError("Workspace not found.")
        await self._workspaces.delete(workspace)

    # --- membership ------------------------------------------------------------
    async def list_members(
        self, workspace_id: UUID, user_id: UUID
    ) -> list[tuple[WorkspaceMember, str, str]]:
        await self.require_member(workspace_id, user_id)
        members = await self._workspaces.list_members(workspace_id)
        enriched: list[tuple[WorkspaceMember, str, str]] = []
        for member in members:
            user = await self._users.get_by_id(member.user_id)
            if user:
                enriched.append((member, user.email, user.full_name))
        return enriched

    async def add_member(
        self, workspace_id: UUID, actor_id: UUID, data: MemberAdd
    ) -> tuple[WorkspaceMember, str, str]:
        await self.require_role(workspace_id, actor_id, {Role.OWNER})
        user = await self._users.get_by_email(data.email)
        if not user:
            raise NotFoundError("No user found with that email.")
        existing = await self._workspaces.get_member(workspace_id, user.id)
        if existing:
            raise ConflictError("User is already a member of this workspace.")
        member = await self._workspaces.add_member(
            WorkspaceMember(
                workspace_id=workspace_id, user_id=user.id, role=data.role
            )
        )
        return member, user.email, user.full_name

    async def update_member(
        self, workspace_id: UUID, actor_id: UUID, target_user_id: UUID, data: MemberUpdate
    ) -> tuple[WorkspaceMember, str, str]:
        await self.require_role(workspace_id, actor_id, {Role.OWNER})
        member = await self._workspaces.get_member(workspace_id, target_user_id)
        if not member:
            raise NotFoundError("Member not found.")
        workspace = await self._workspaces.get_by_id(workspace_id)
        if (
            workspace
            and workspace.owner_id == target_user_id
            and data.role != Role.OWNER
        ):
            raise ValidationError("The workspace owner's role cannot be changed.")
        member.role = data.role
        member = await self._workspaces.add_member(member)
        user = await self._users.get_by_id(target_user_id)
        return member, user.email, user.full_name  # type: ignore[union-attr]

    async def remove_member(
        self, workspace_id: UUID, actor_id: UUID, target_user_id: UUID
    ) -> None:
        await self.require_role(workspace_id, actor_id, {Role.OWNER})
        workspace = await self._workspaces.get_by_id(workspace_id)
        if workspace and workspace.owner_id == target_user_id:
            raise ValidationError("The workspace owner cannot be removed.")
        member = await self._workspaces.get_member(workspace_id, target_user_id)
        if not member:
            raise NotFoundError("Member not found.")
        await self._workspaces.remove_member(member)
