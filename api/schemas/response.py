from pydantic import BaseModel, Field
from typing import Optional


class Response(BaseModel):
    message: str = Field(..., example="Success")
    data: Optional[dict] = None
