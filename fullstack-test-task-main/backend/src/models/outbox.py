from datetime import datetime
from typing import Dict, Any
from sqlalchemy.dialects.postgresql import JSON
from src.infrastructure.config import Base
from sqlalchemy import DateTime, func, Integer
from sqlalchemy.orm import Mapped, mapped_column


class OutboxMessage(Base):
    __tablename__ = "outbox_messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_id: Mapped[str]
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    queue: Mapped[str]
    processed: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
