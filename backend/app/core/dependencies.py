from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.embeddings.minilm_embedder import get_embedder
from app.ai.llm.ollama_client import get_llm_client
from app.core.constants import TokenType
from app.core.exceptions import UnauthorizedError
from app.core.security import decode_token
from app.database.session import get_db
from app.models.user import User
from app.rag.retriever import Retriever
from app.rag.rag_pipeline import RAGPipeline
from app.repositories.implementations.chat_repository import ChatRepository
from app.repositories.implementations.document_repository import DocumentRepository
from app.repositories.implementations.summary_repository import SummaryRepository
from app.repositories.implementations.tag_repository import TagRepository
from app.repositories.implementations.token_repository import TokenRepository
from app.repositories.implementations.user_repository import UserRepository
from app.repositories.implementations.vector_repository import ChromaVectorRepository
from app.repositories.implementations.workspace_repository import WorkspaceRepository
from app.services.auth_service import AuthService
from app.services.chat_service import ChatService
from app.services.comparison_service import ComparisonService
from app.services.document_service import DocumentService
from app.services.flashcard_service import FlashcardService
from app.services.quiz_service import QuizService
from app.services.search_service import SearchService
from app.services.summary_service import SummaryService
from app.services.tag_service import TagService
from app.services.user_service import UserService
from app.services.workspace_service import WorkspaceService

_bearer = HTTPBearer(auto_error=False)

DbSession = Annotated[AsyncSession, Depends(get_db)]


# --- Authentication ------------------------------------------------------------
async def get_current_user(
    session: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> User:
    if credentials is None:
        raise UnauthorizedError("Authentication required.")
    user_id = decode_token(credentials.credentials, TokenType.ACCESS)
    user = await UserRepository(session).get_by_id(user_id)
    if not user or not user.is_active:
        raise UnauthorizedError("User not found or inactive.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


# --- Service providers (composition root) -------------------------------------
def get_auth_service(session: DbSession) -> AuthService:
    return AuthService(UserRepository(session), TokenRepository(session))


def get_user_service(session: DbSession) -> UserService:
    return UserService(UserRepository(session))


def get_workspace_service(session: DbSession) -> WorkspaceService:
    return WorkspaceService(WorkspaceRepository(session), UserRepository(session))


def get_document_service(session: DbSession) -> DocumentService:
    return DocumentService(
        DocumentRepository(session),
        TagRepository(session),
        WorkspaceService(WorkspaceRepository(session), UserRepository(session)),
    )


def get_tag_service(session: DbSession) -> TagService:
    return TagService(
        TagRepository(session),
        WorkspaceService(WorkspaceRepository(session), UserRepository(session)),
    )


def _build_retriever() -> Retriever:
    return Retriever(get_embedder(), ChromaVectorRepository())


def _build_rag_pipeline() -> RAGPipeline:
    return RAGPipeline(_build_retriever(), get_llm_client())


def get_chat_service(session: DbSession) -> ChatService:
    return ChatService(
        ChatRepository(session),
        DocumentRepository(session),
        WorkspaceService(WorkspaceRepository(session), UserRepository(session)),
        _build_rag_pipeline(),
    )


def get_summary_service(session: DbSession) -> SummaryService:
    return SummaryService(
        SummaryRepository(session),
        DocumentRepository(session),
        WorkspaceService(WorkspaceRepository(session), UserRepository(session)),
        get_llm_client(),
    )


def get_search_service(session: DbSession) -> SearchService:
    return SearchService(
        _build_retriever(),
        DocumentRepository(session),
        WorkspaceService(WorkspaceRepository(session), UserRepository(session)),
    )


def get_comparison_service(session: DbSession) -> ComparisonService:
    return ComparisonService(
        DocumentRepository(session),
        WorkspaceService(WorkspaceRepository(session), UserRepository(session)),
        get_llm_client(),
    )


def get_quiz_service(session: DbSession) -> QuizService:
    return QuizService(
        DocumentRepository(session),
        WorkspaceService(WorkspaceRepository(session), UserRepository(session)),
        get_llm_client(),
    )


def get_flashcard_service(session: DbSession) -> FlashcardService:
    return FlashcardService(
        DocumentRepository(session),
        WorkspaceService(WorkspaceRepository(session), UserRepository(session)),
        get_llm_client(),
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
WorkspaceServiceDep = Annotated[WorkspaceService, Depends(get_workspace_service)]
DocumentServiceDep = Annotated[DocumentService, Depends(get_document_service)]
TagServiceDep = Annotated[TagService, Depends(get_tag_service)]
ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
SummaryServiceDep = Annotated[SummaryService, Depends(get_summary_service)]
SearchServiceDep = Annotated[SearchService, Depends(get_search_service)]
ComparisonServiceDep = Annotated[
    ComparisonService, Depends(get_comparison_service)
]
QuizServiceDep = Annotated[QuizService, Depends(get_quiz_service)]
FlashcardServiceDep = Annotated[
    FlashcardService, Depends(get_flashcard_service)
]
