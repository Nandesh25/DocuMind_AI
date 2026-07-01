from fastapi import APIRouter

from app.api.routers import (
    auth_router,
    chat_router,
    comparison_router,
    document_router,
    flashcard_router,
    quiz_router,
    search_router,
    summary_router,
    tag_router,
    user_router,
    workspace_router,
)

api_router = APIRouter()
api_router.include_router(auth_router.router)
api_router.include_router(user_router.router)
api_router.include_router(workspace_router.router)
api_router.include_router(document_router.router)
api_router.include_router(chat_router.router)
api_router.include_router(summary_router.router)
api_router.include_router(search_router.router)
api_router.include_router(tag_router.router)
api_router.include_router(comparison_router.router)
api_router.include_router(quiz_router.router)
api_router.include_router(flashcard_router.router)
