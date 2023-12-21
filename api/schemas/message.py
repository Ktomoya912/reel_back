from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    title: str
    message: str = Field(..., max_length=1000)
    type: str = Field(..., max_length=1)


class MessageCreate(MessageBase):
    pass


class Message(MessageBase):
    id: int

    class Config:
        orm_mode = True


class MessageBoxBase(BaseModel):
    user_id: int
    message_id: int
    is_read: bool = False
