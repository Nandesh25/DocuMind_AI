from uuid import UUID

from fastapi import APIRouter, Response, status

from app.core.dependencies import CurrentUser, SummaryServiceDep
from app.schemas.summary_schema import SummaryCreate, SummaryResponse

router = APIRouter(tags=["Summaries"])


@router.post(
    "/documents/{document_id}/summaries", response_model=SummaryResponse
)
async def generate_summary(
    document_id: UUID,
    data: SummaryCreate,
    current_user: CurrentUser,
    service: SummaryServiceDep,
    response: Response,
) -> SummaryResponse:
    summary, created = await service.generate(document_id, current_user.id, data)
    response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return SummaryResponse.model_validate(summary)


@router.get(
    "/documents/{document_id}/summaries", response_model=list[SummaryResponse]
)
async def list_summaries(
    document_id: UUID, current_user: CurrentUser, service: SummaryServiceDep
) -> list[SummaryResponse]:
    summaries = await service.list(document_id, current_user.id)
    return [SummaryResponse.model_validate(s) for s in summaries]


@router.delete("/summaries/{summary_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_summary(
    summary_id: UUID, current_user: CurrentUser, service: SummaryServiceDep
) -> None:
    await service.delete(summary_id, current_user.id)
    return None
