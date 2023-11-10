from typing import Optional
from pydantic import BaseModel, Field
from .company import Company
from datetime import datetime


class UserBase(BaseModel):
    username: str
    password: str
    email: str
    gender: Optional[str] = Field(
        "",
        example="男",
        description="性别",
        max_length=2,
    )
    birthday: datetime
    user_type: str = Field(
        "default",
        example="user",
        description="ユーザータイプ",
    )


class User(UserBase):
    id: int
    company: Optional[Company] = None

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    pass


class UserCreateResponse(UserCreate):
    id: int

    class Config:
        orm_mode = True
