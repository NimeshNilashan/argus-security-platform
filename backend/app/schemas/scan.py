# Defines the data format used when creating and returning scans.

import uuid
from datetime import datetime

from pydantic import BaseModel


# Data received when starting a new scan.
class ScanCreate(BaseModel):
    user_id: uuid.UUID
    module: str
    target: str


# Data sent back to the frontend.
class ScanResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    module: str
    target: str
    status: str
    started_at: datetime
    completed_at: datetime | None

    class Config:
        from_attributes = True