from typing import List

from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    title: str = Field(..., max_length=255, description="タイトル")
    message: str = Field(..., max_length=1000, description="メッセージ")
    type: str = Field(
        ..., max_length=1, description="J:ジョブ, E:イベント", examples=["J", "E"]
    )


class MessageCreate(MessageBase):
    user_list: List[int]


class Message(MessageBase):
    id: int

    class Config:
        orm_mode = True


class MessageBoxBase(BaseModel):
    user_id: int
    message_id: int
    is_read: bool = False
