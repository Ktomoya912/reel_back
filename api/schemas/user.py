from typing import Optional
from pydantic import BaseModel, Field
from .company import Company


class UserBase(BaseModel):
    name: str
    password: str
    email: str
    gender: Optional[str] = Field(
        "",
        example="男",
        description="性别",
        max_length=2,
    )
    birthday: Optional[str] = Field(
        "",
        example="1990-01-01",
        description="誕生日",
    )
    company: Optional[Company]


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    pass


class UserCreateResponse(UserCreate):
    id: int

    class Config:
        orm_mode = True
