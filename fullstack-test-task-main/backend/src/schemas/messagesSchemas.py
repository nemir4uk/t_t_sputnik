import enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ScanStatus(str, enum.Enum):
    uploaded = "UPLOADED"
    success_check = "SUCCESS_CHECK"
    failed_check = "FAILED_CHECK"


class FilePayload(BaseModel):
    file_id: UUID
    original_name: str
    stored_name: str
    mime_type: str
    size: int
    scan_details: Optional[str] = None
    processing_status: Optional[str] = None
    requires_attention: Optional[bool] = None
    metadata_json: Optional[dict] = None
    scan_status: Optional[ScanStatus] = None
    # idempotency_key: str
