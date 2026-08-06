# Data structures for File Integrity API.

import uuid

from pydantic import BaseModel


class FIMBaselineCreate(BaseModel):
    user_id: uuid.UUID
    custom_name: str


class FIMVerifyRequest(BaseModel):
    baseline_id: uuid.UUID