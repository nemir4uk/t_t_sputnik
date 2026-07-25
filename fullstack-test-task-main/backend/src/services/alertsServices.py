import logging
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.config import settings
from src.models.alert import Alert
from src.services.queries.alertQueries import list_alerts_query

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


async def list_alerts(
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
) -> list[Alert]:
    logger.debug('list_alerts start')
    result = await list_alerts_query(session, limit, offset)
    logger.debug('list_alerts end')
    return list(result.scalars().all())

