# Defines the structure of security findings.

import uuid
from datetime import datetime

from pydantic import BaseModel


# Data received when creating a finding.
class FindingCreate(BaseModel):

    scan_id: uuid.UUID
    severity: str
    title: str
    description: str
    data: dict | None = None


# Data returned to frontend.
class FindingResponse(BaseModel):

    id: uuid.UUID
    scan_id: uuid.UUID
    severity: str
    title: str
    description: str
    data: dict | None
    created_at: datetime


    class Config:
        from_attributes = True  