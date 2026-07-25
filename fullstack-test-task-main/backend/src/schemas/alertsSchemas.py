from uuid import UUID
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class AlertItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    file_id: UUID
    level: str
    message: str
    created_at: datetime
