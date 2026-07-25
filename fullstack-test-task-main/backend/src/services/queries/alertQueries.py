from sqlalchemy import select
from src.models.alert import Alert


async def list_alerts_query(session, limit, offset):
    list_alerts_stmt = (
        select(Alert)
        .order_by(Alert.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return await session.execute(list_alerts_stmt)