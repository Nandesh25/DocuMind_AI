from app.core.logging import get_logger
from app.database.session import engine
from app.models import Base

logger = get_logger(__name__)


async def init_models() -> None:
    """Create all tables if they do not exist.

    Convenience for containerized/dev startup (AUTO_CREATE_TABLES=true).
    Production should use Alembic migrations instead.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ensured (create_all).")