from typing import Optional

from pydantic import BaseModel


class SaveRequest(BaseModel):
    value: str
    ttl_seconds: Optional[int] = None


class SaveResponse(BaseModel):
    key: str
    status: str


class RetrieveResponse(BaseModel):
    key: str
    value: str
