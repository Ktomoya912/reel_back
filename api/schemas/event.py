from typing import Optional
from pydantic import BaseModel, Field


class EventBase(BaseModel):
    name: str
    postal_code: str
    prefecture: str
    city: str
    address: str
    phone_number: str
    email: str
    homepage: Optional[str] = Field(
        "",
        example="https://example.com",
        description="ホームページ",
    )
    period: str
    participation_fee: str  # 参加費
    capacity: str  # 定員
    caution: str
    additional_message: str
    event_description: str


class Event(EventBase):
    id: int

    class Config:
        orm_mode = True
