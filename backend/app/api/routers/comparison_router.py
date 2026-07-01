from uuid import UUID

from fastapi import APIRouter

from app.core.dependencies import ComparisonServiceDep, CurrentUser
from app.schemas.comparison_schema import CompareRequest, ComparisonResponse

router = APIRouter(tags=["Comparison"])


@router.post(
    "/workspaces/{workspace_id}/compare", response_model=ComparisonResponse
)
async def compare_documents(
    workspace_id: UUID,
    data: CompareRequest,
    current_user: CurrentUser,
    service: ComparisonServiceDep,
) -> ComparisonResponse:
    """Compare two indexed documents: similarity score + structured analysis."""
    return await service.compare(workspace_id, current_user.id, data)
