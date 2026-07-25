from typing import List

from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.sessions import get_async_session
from src.schemas.alertsSchemas import AlertItem
from src.services.alertsServices import list_alerts

alerts_router = APIRouter()

@alerts_router.get("/alerts", response_model=List[AlertItem])
async def list_alerts_view(
        limit: int = 100,
        offset: int = 0,
        session: AsyncSession = Depends(get_async_session)
):
    return await list_alerts(limit=limit, offset=offset, session=session)

