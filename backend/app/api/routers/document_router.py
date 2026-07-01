from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse

from app.core.constants import DocumentStatus
from app.core.dependencies import CurrentUser, DocumentServiceDep
from app.schemas.common import PageParams, PageResponse
from app.schemas.document_schema import DocumentResponse, DocumentUpdate
from app.services.ingestion_service import IngestionService

router = APIRouter(tags=["Documents"])


@router.post(
    "/workspaces/{workspace_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_document(
    workspace_id: UUID,
    current_user: CurrentUser,
    service: DocumentServiceDep,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
) -> DocumentResponse:
    document = await service.upload(workspace_id, current_user.id, file, title)
    background_tasks.add_task(IngestionService().ingest, document.id)
    return DocumentResponse.model_validate(document)


@router.get(
    "/workspaces/{workspace_id}/documents",
    response_model=PageResponse[DocumentResponse],
)
async def list_documents(
    workspace_id: UUID,
    current_user: CurrentUser,
    service: DocumentServiceDep,
    params: PageParams = Depends(),
    status_filter: DocumentStatus | None = Query(default=None, alias="status"),
    q: str | None = Query(default=None),
) -> PageResponse[DocumentResponse]:
    items, total = await service.list(
        workspace_id, current_user.id, params.offset, params.size, status_filter, q
    )
    return PageResponse(
        items=[DocumentResponse.model_validate(d) for d in items],
        total=total,
        page=params.page,
        size=params.size,
    )


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID, current_user: CurrentUser, service: DocumentServiceDep
) -> DocumentResponse:
    document = await service.get(document_id, current_user.id)
    return DocumentResponse.model_validate(document)


@router.get("/documents/{document_id}/download")
async def download_document(
    document_id: UUID, current_user: CurrentUser, service: DocumentServiceDep
) -> FileResponse:
    document = await service.get(document_id, current_user.id)
    return FileResponse(
        path=document.storage_path,
        media_type=document.mime_type,
        filename=document.original_filename,
    )


@router.patch("/documents/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: UUID,
    data: DocumentUpdate,
    current_user: CurrentUser,
    service: DocumentServiceDep,
) -> DocumentResponse:
    document = await service.update(document_id, current_user.id, data)
    return DocumentResponse.model_validate(document)


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID, current_user: CurrentUser, service: DocumentServiceDep
) -> None:
    await service.delete(document_id, current_user.id)
    return None


@router.post(
    "/documents/{document_id}/reindex",
    response_model=DocumentResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def reindex_document(
    document_id: UUID,
    current_user: CurrentUser,
    service: DocumentServiceDep,
    background_tasks: BackgroundTasks,
) -> DocumentResponse:
    document = await service.reindex(document_id, current_user.id)
    background_tasks.add_task(IngestionService().ingest, document.id)
    return DocumentResponse.model_validate(document)
