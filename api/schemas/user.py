from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel, Field, field_serializer
from datetime import datetime
from hashlib import sha256

from .company import Company

# if TYPE_CHECKING:


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

    @field_serializer("password")
    def password_hash(self, v):
        return sha256(v.encode(encoding="utf-8")).hexdigest()


class User(UserBase):
    id: int
    company: Optional["Company"] = Field(
        None,
        example={},
        description="会社情報",
    )
    event_bookmarks: Optional[list] = Field(
        [],
        example=[],
        description="お気に入り(イベント)",
    )
    job_bookmarks: Optional[list] = Field(
        [],
        example=[],
        description="お気に入り(求人)",
    )
    applications: Optional[list] = Field(
        [],
        example=[],
        description="応募履歴(求人)",
    )
    watch_jobs: Optional[list] = Field(
        [],
        example=[],
        description="閲覧履歴(求人)",
    )
    reviews: Optional[list] = Field(
        [],
        example=[],
        description="レビュー",
    )
    messages: Optional[list] = Field(
        [],
        example=[],
        description="メッセージ",
    )

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    pass


class UserCreateResponse(UserCreate):
    id: int

    class Config:
        orm_mode = True
