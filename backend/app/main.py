from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routers import api_router
from app.config.settings import settings
from app.core.exceptions import AppException
from app.core.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Path(settings.STORAGE_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.CHROMA_DIR).mkdir(parents=True, exist_ok=True)
    if settings.AUTO_CREATE_TABLES:
        from app.database.init_db import init_models

        await init_models()
    logger.info(
        "%s started (env=%s, llm=%s/%s, embeddings=%s)",
        settings.APP_NAME,
        settings.APP_ENV,
        settings.LLM_PROVIDER,
        settings.OPENAI_MODEL
        if settings.LLM_PROVIDER.lower() == "openai"
        else settings.OLLAMA_MODEL,
        settings.EMBEDDING_MODEL,
    )
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        debug=settings.DEBUG,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url="/docs",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(AppException)
    async def _app_exception_handler(
        _: Request, exc: AppException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "code": exc.code},
        )

    @app.get("/health", tags=["Health"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    return app


app = create_app()
